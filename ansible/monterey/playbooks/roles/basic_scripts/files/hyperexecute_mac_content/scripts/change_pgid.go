package main

import (
	"os"
	"os/exec"
	"syscall"
)

func main() {
	// Set the process group ID and execute the specified command
	syscall.Setpgid(0, 0)
	cmd := exec.Command(os.Args[1], os.Args[2:]...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Run()
}
