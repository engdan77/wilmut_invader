#!/bin/bash

# Tested 2025-03-01 with Python 3.12
# When tested work on x86 and not arm64 architecture

# Make directories for Buildozer recipes etc
mkdir -p game/p4a-recipes/pygame-ce/
mv -f buildozer.spec game/buildozer.spec
mv -f -r ../src/wilmut_invader/* game/
mv -f pygame-ce-recipe.py game/p4a-recipes/pygame-ce/__init__.py

# Build Docker image
docker build --tag=kivy/buildozer .

# Create docker
mkdir -p docker/{buildozer,gradle}
docker run -it --rm \
    -u "$(id -u):$(id -g)" \
    -v "$(pwd)/docker/buildozer":/home/user/.buildozer \
    -v "$(pwd)/docker/gradle":/home/user/.gradle \
    -v "$(pwd)/game":/home/user/hostcwd \
    kivy/buildozer -v android debug

  echo "apk written to $(pwd)/game/bin"
  mv $(pwd)/game/bin/*.apk .
  rm -rf -v $(pwd)/game