{ pkgs, ... }:

{
  devenv.warnOnNewVersion = false;

  packages = with pkgs; [
    libxml2
    libxslt
  ];

  languages.python = {
    enable = true;
    package = pkgs.python314;
    uv.enable = true;
  };
}
