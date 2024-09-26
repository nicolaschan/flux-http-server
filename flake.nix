{
  description = "A Python project with aiohttp";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        system = "x86_64-linux";
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            cudaSupport = true;
          };
        };
        pythonPackages = pkgs.python3Packages;
      in {
        packages.default = pythonPackages.buildPythonApplication {
          pname = "flux-api";
          version = "0.1.0";
          src = ./.;
          propagatedBuildInputs = with pythonPackages; [
            aiohttp
          ];
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            python311Packages.accelerate
            python311Packages.aiohttp
            python311Packages.diffusers
            python311Packages.huggingface-hub
            python311Packages.transformers
            python311Packages.pytorch-bin
            python311Packages.pip
            python311Packages.sentencepiece
          ];
        };
      }
    );
}
