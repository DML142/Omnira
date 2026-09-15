package main

import (
	"context"
	"errors"
	"log/slog"
	"net"
	"net/netip"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/DML142/Omnira/services/gateway/internal/server"
)

func listenAddress() (string, error) {
	address := os.Getenv("OMNIRA_GATEWAY_ADDR")
	if address == "" {
		address = "127.0.0.1:8080"
	}
	parsed, err := netip.ParseAddrPort(address)
	if err != nil || parsed.Port() == 0 || !parsed.Addr().IsLoopback() {
		return "", errors.New("OMNIRA_GATEWAY_ADDR must be a loopback IP address and port between 1 and 65535")
	}
	return parsed.String(), nil
}

func run(logger *slog.Logger) error {
	address, err := listenAddress()
	if err != nil {
		return err
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	listener, err := net.Listen("tcp", address)
	if err != nil {
		return err
	}
	logger.Info("gateway listening", "address", listener.Addr().String())
	err = server.Serve(ctx, server.New(server.Handler(logger)), listener, 10*time.Second)
	if err == nil {
		logger.Info("gateway stopped")
	}
	return err
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	if err := run(logger); err != nil {
		logger.Error("gateway failed", "error", err)
		os.Exit(1)
	}
}
