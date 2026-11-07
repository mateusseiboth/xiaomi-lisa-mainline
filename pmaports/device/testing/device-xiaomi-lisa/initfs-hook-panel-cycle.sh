#!/bin/sh
# The first DSI link bring-up after the bootloader hand-off is broken on lisa:
# the panel stays dark and ignores DCS commands until the link is powered off
# and on again. Do that once, as soon as the msm framebuffer shows up, so the
# boot console is visible and the compositor's first modeset works.

fb=/sys/class/graphics/fb0

for _ in $(seq 1 100); do
	[ "$(cat "$fb/name" 2>/dev/null)" = "msmdrmfb" ] && break
	sleep 0.1
done

[ "$(cat "$fb/name" 2>/dev/null)" = "msmdrmfb" ] || exit 0

echo 1 > "$fb/blank"
sleep 0.2
echo 0 > "$fb/blank"
