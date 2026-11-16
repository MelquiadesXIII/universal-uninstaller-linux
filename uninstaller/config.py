"""Security configuration and exit codes."""

from __future__ import annotations

from pathlib import Path

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2
EXIT_NOT_FOUND = 3
EXIT_AMBIGUOUS = 4
EXIT_CANCELLED = 5
EXIT_PARTIAL = 6
EXIT_BLOCKED = 7

CRITICAL_PATTERNS = (
    "apt",
    "apt-*",
    "dpkg",
    "libc6",
    "libc-bin",
    "bash",
    "coreutils",
    "util-linux",
    "systemd",
    "systemd-*",
    "udev",
    "dbus",
    "dbus-*",
    "sudo",
    "sudo-rs",
    "login",
    "passwd",
    "grub-*",
    "shim-*",
    "linux-image-*",
    "linux-modules-*",
    "linux-headers-*",
    "initramfs-tools*",
    "sddm",
    "sddm-*",
    "network-manager",
    "network-manager-*",
    "netplan.io",
    "plasma-desktop",
    "plasma-workspace",
    "plasma-*",
    "kwin*",
    "kde-plasma-desktop",
    "ubuntu-desktop*",
    "*-desktop",
    "xorg",
    "xserver-xorg*",
    "wayland*",
    "libwayland*",
    "mesa-*",
    "nvidia-*",
    "libnvidia-*",
    "dolphin",
    "dolphin-*",
    "konsole",
    "kde-*",
    "dracut*",
    "ubuntu-minimal",
    "ubuntu-standard",
)

EXTRA_CONFIRM_PATTERNS = (
    "curl",
    "wget",
    "git",
    "python3",
    "python3-*",
    "openssh-*",
    "ca-certificates",
    "gnupg*",
    "snapd",
    "flatpak",
    "firefox",
    "cups*",
    "pipewire*",
    "pulseaudio*",
    "bluez*",
)

USER_TRASH_ROOTS = (
    ".local/share/applications",
    ".local/share/icons",
    ".local/bin",
    ".local",
    "Applications",
    "Descargas",
    "Downloads",
    ".opencode",
)

ROOT_DELETE_ROOTS = (
    "/opt",
    "/usr/local/bin",
    "/usr/local/lib",
    "/usr/local/share",
    "/etc/systemd/system",
)

APT_SUITES = {
    "wine": (
        "wine",
        "wine32*",
        "wine64*",
        "libwine*",
        "fonts-wine",
        "winehq-*",
        "wine-stable*",
        "wine-devel*",
        "wine-staging*",
    ),
    "docker": (
        "docker-ce",
        "docker-ce-cli",
        "docker-ce-rootless-extras",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin",
        "docker-model-plugin",
        "docker.io",
        "docker-compose",
    ),
    "postgresql": (
        "postgresql",
        "postgresql-[0-9]*",
        "postgresql-client-*",
        "postgresql-contrib",
        "postgresql-common",
        "postgresql-client-common",
    ),
    "pgadmin": ("pgadmin4", "pgadmin4-*"),
    "dotnet": (
        "dotnet-sdk-*",
        "dotnet-runtime-*",
        "aspnetcore-runtime-*",
        "dotnet-host*",
        "dotnet-hostfxr-*",
        "dotnet-apphost-pack-*",
        "dotnet-targeting-pack-*",
        "dotnet-templates-*",
        "netstandard-targeting-pack-*",
    ),
    "r-base": (
        "r-base",
        "r-base-core",
        "r-base-dev",
        "r-base-html",
        "r-recommended",
        "r-doc-*",
    ),
    "mkvtoolnix": ("mkvtoolnix", "mkvtoolnix-gui"),
}


def log_path(home: Path | None = None) -> Path:
    """Return the log path for the specified HOME."""

    base = home if home is not None else Path.home()
    return base / ".local" / "state" / "uninstall" / "uninstall.log"
