package server

import (
	"context"
	"errors"
	"io"
	"log/slog"
	"net"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestHealth(t *testing.T) {
	handler := Handler(slog.New(slog.NewTextHandler(io.Discard, nil)))
	for _, tc := range []struct {
		method, path string
		status       int
		body         string
	}{
		{"GET", "/healthz", 200, `{"status":"ok"}`},
		{"POST", "/healthz", 405, `{"error":{"code":"method_not_allowed"}}`},
		{"GET", "/missing?token=private", 404, `{"error":{"code":"not_found"}}`},
	} {
		t.Run(tc.method+tc.path, func(t *testing.T) {
			response := httptest.NewRecorder()
			handler.ServeHTTP(response, httptest.NewRequest(tc.method, tc.path, nil))
			if response.Code != tc.status || strings.TrimSpace(response.Body.String()) != tc.body {
				t.Fatalf("got %d %s", response.Code, response.Body.String())
			}
			if response.Header().Get("Content-Type") != "application/json; charset=utf-8" {
				t.Fatal("expected JSON content type")
			}
		})
	}
}

func TestShutdownDrainsActiveRequest(t *testing.T) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	started, release := make(chan struct{}), make(chan struct{})
	srv := New(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		close(started)
		<-release
		_, _ = io.WriteString(w, "completed")
	}))
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	done := make(chan error, 1)
	go func() { done <- Serve(ctx, srv, listener, time.Second) }()
	result := make(chan string, 1)
	go func() {
		client := &http.Client{Timeout: 3 * time.Second}
		res, e := client.Get("http://" + listener.Addr().String())
		if e != nil {
			result <- e.Error()
			return
		}
		defer func() { _ = res.Body.Close() }()
		body, e := io.ReadAll(res.Body)
		if e != nil {
			result <- e.Error()
			return
		}
		result <- string(body)
	}()
	select {
	case <-started:
	case <-time.After(3 * time.Second):
		t.Fatal("request did not start")
	}
	cancel()
	select {
	case err := <-done:
		t.Fatalf("shutdown returned before request drained: %v", err)
	case <-time.After(30 * time.Millisecond):
	}
	close(release)
	select {
	case body := <-result:
		if body != "completed" {
			t.Fatalf("request lost: %s", body)
		}
	case <-time.After(3 * time.Second):
		t.Fatal("request timed out")
	}
	select {
	case err := <-done:
		if err != nil {
			t.Fatal(err)
		}
	case <-time.After(3 * time.Second):
		t.Fatal("shutdown timed out")
	}
}

func TestShutdownDeadline(t *testing.T) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	started, handlerDone := make(chan struct{}), make(chan struct{})
	srv := New(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		close(started)
		<-r.Context().Done()
		close(handlerDone)
	}))
	t.Cleanup(func() { _ = srv.Close() })
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	done, clientDone := make(chan error, 1), make(chan error, 1)
	go func() { done <- Serve(ctx, srv, listener, 20*time.Millisecond) }()
	go func() {
		c := &http.Client{Timeout: 5 * time.Second}
		res, err := c.Get("http://" + listener.Addr().String())
		if err == nil {
			_ = res.Body.Close()
		}
		clientDone <- err
	}()
	select {
	case <-started:
	case <-time.After(3 * time.Second):
		t.Fatal("request did not start")
	}
	cancel()
	select {
	case err := <-done:
		if !errors.Is(err, context.DeadlineExceeded) {
			t.Fatalf("expected shutdown deadline: %v", err)
		}
	case <-time.After(time.Second):
		t.Fatal("shutdown not bounded")
	}
	select {
	case <-handlerDone:
	case <-time.After(time.Second):
		t.Fatal("expired shutdown did not cancel active handler")
	}
	select {
	case err := <-clientDone:
		if err == nil {
			t.Fatal("expected active connection to close without response")
		}
	case <-time.After(time.Second):
		t.Fatal("active client connection left open")
	}
}
