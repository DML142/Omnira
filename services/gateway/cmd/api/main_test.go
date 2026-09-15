package main

import "testing"

func TestListenAddress(t *testing.T) {
	for _, tc := range []struct {
		value string
		valid bool
	}{
		{"", true}, {"127.0.0.1:8081", true}, {"[::1]:8080", true},
		{"0.0.0.0:8080", false}, {"192.168.1.10:8080", false}, {"localhost:8080", false}, {":8080", false},
		{"127.0.0.1:0", false}, {"127.0.0.1:65536", false}, {"127.0.0.1:abc", false},
	} {
		t.Run(tc.value, func(t *testing.T) {
			t.Setenv("OMNIRA_GATEWAY_ADDR", tc.value)
			addr, err := listenAddress()
			if (err == nil) != tc.valid {
				t.Fatalf("address %q: %v", tc.value, err)
			}
			if tc.value == "" && addr != "127.0.0.1:8080" {
				t.Fatalf("unsafe default %s", addr)
			}
		})
	}
}
