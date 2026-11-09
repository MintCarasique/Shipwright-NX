# Local build environment for the Switch port (same as CI)
#   docker build -t shipwright-nx-builder -f tools/switch/Dockerfile tools/switch
FROM devkitpro/devkita64:latest
# portlibs ships tinyxml2 6.0.0, whose header shadows the 11.0.0 that libultraship builds
RUN dkp-pacman -Rdd --noconfirm switch-tinyxml2 && git config --global --add safe.directory '*'
