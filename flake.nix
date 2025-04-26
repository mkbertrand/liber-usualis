{
    description = "Python Bottle DevShell";

    inputs = {
        determinate.url = "https://flakehub.com/f/DeterminateSystems/determinate/0.1";
        nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2411.0";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils, determinate, ... }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs {
                    inherit system;
                };

                pythonEnv = pkgs.python3.withPackages (ps: with ps; [
                    bottle
                    pytest
                    diff-match-patch
                    requests
                ]);
            in {
                devShells.default = pkgs.mkShell {
                    name = "libu-dev-shell";

                    packages = [
                        pythonEnv
                    ];
                };
            });
}

