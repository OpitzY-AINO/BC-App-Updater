{pkgs}: {
  deps = [
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
    pkgs.xterm
    pkgs.tigervnc
    pkgs.xvfb-run
  ];
}
