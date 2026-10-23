/*
 * pointerwall - confine the X11 pointer to the monitor it is already on.
 *
 * Places XFixes pointer barriers around the perimeter of every Xinerama
 * monitor, so relative pointer motion can never cross a monitor boundary.
 * Pointer warps are not affected by barriers, so a window manager that warps
 * the pointer when keyboard focus moves to another output (i3's
 * "mouse_warping output") still puts the pointer on the newly focused screen.
 *
 * SIGUSR1 toggles the barriers off and on, for dragging something across a
 * boundary. Exiting removes them.
 */

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <X11/Xlib.h>
#include <X11/extensions/Xfixes.h>
#include <X11/extensions/Xinerama.h>

#define MAX_MONITORS 16
#define MAX_BARRIERS (MAX_MONITORS * 4)
#define POLL_SECONDS 3

struct layout {
	int count;
	XineramaScreenInfo monitor[MAX_MONITORS];
};

static int read_layout(Display *dpy, struct layout *out);
static void create_barriers(Display *dpy, const struct layout *layout);
static void destroy_barriers(Display *dpy);

static PointerBarrier barrier[MAX_BARRIERS];
static int barrier_count = 0;

static volatile sig_atomic_t quit_requested = 0;
static volatile sig_atomic_t toggle_requested = 0;

static void on_quit(int signal_number)
{
	(void)signal_number;
	quit_requested = 1;
}

static void on_toggle(int signal_number)
{
	(void)signal_number;
	toggle_requested = 1;
}

int main(void)
{
	Display *dpy = XOpenDisplay(NULL);
	if (!dpy) {
		fprintf(stderr, "pointerwall: cannot open display\n");
		return 1;
	}

	int major = 0, minor = 0;
	if (!XFixesQueryVersion(dpy, &major, &minor) || major < 5) {
		fprintf(stderr, "pointerwall: server lacks XFixes 5 pointer barriers (got %d.%d)\n",
			major, minor);
		XCloseDisplay(dpy);
		return 1;
	}

	if (!XineramaIsActive(dpy)) {
		fprintf(stderr, "pointerwall: Xinerama inactive, no monitor layout to read\n");
		XCloseDisplay(dpy);
		return 1;
	}

	struct layout layout;
	if (!read_layout(dpy, &layout)) {
		fprintf(stderr, "pointerwall: cannot read monitor layout\n");
		XCloseDisplay(dpy);
		return 1;
	}

	signal(SIGINT, on_quit);
	signal(SIGTERM, on_quit);
	signal(SIGUSR1, on_toggle);

	create_barriers(dpy, &layout);
	printf("pointerwall: %d barriers over %d monitors\n", barrier_count, layout.count);
	fflush(stdout);

	int enabled = 1;

	while (!quit_requested) {
		struct timespec interval = { POLL_SECONDS, 0 };
		nanosleep(&interval, NULL);

		if (quit_requested)
			break;

		if (toggle_requested) {
			toggle_requested = 0;
			enabled = !enabled;
			if (enabled) {
				create_barriers(dpy, &layout);
				printf("pointerwall: enabled\n");
			} else {
				destroy_barriers(dpy);
				printf("pointerwall: disabled\n");
			}
			fflush(stdout);
			continue;
		}

		if (!enabled)
			continue;

		struct layout current;
		if (!read_layout(dpy, &current))
			continue;

		if (memcmp(&current, &layout, sizeof(layout)) == 0)
			continue;

		layout = current;
		destroy_barriers(dpy);
		create_barriers(dpy, &layout);
		printf("pointerwall: layout changed, %d barriers over %d monitors\n",
		       barrier_count, layout.count);
		fflush(stdout);
	}

	destroy_barriers(dpy);
	XCloseDisplay(dpy);
	return 0;
}

static int read_layout(Display *dpy, struct layout *out)
{
	int count = 0;
	XineramaScreenInfo *info = XineramaQueryScreens(dpy, &count);
	if (!info)
		return 0;

	if (count > MAX_MONITORS)
		count = MAX_MONITORS;

	memset(out, 0, sizeof(*out));
	out->count = count;
	memcpy(out->monitor, info, (size_t)count * sizeof(XineramaScreenInfo));
	XFree(info);
	return count > 0;
}

static void create_barriers(Display *dpy, const struct layout *layout)
{
	Window root = DefaultRootWindow(dpy);

	for (int i = 0; i < layout->count; i++) {
		int left = layout->monitor[i].x_org;
		int top = layout->monitor[i].y_org;
		int right = left + layout->monitor[i].width;
		int bottom = top + layout->monitor[i].height;

		if (barrier_count + 4 > MAX_BARRIERS)
			return;

		barrier[barrier_count++] =
			XFixesCreatePointerBarrier(dpy, root, left, top, right, top, 0, 0, NULL);
		barrier[barrier_count++] =
			XFixesCreatePointerBarrier(dpy, root, left, bottom, right, bottom, 0, 0, NULL);
		barrier[barrier_count++] =
			XFixesCreatePointerBarrier(dpy, root, left, top, left, bottom, 0, 0, NULL);
		barrier[barrier_count++] =
			XFixesCreatePointerBarrier(dpy, root, right, top, right, bottom, 0, 0, NULL);
	}

	XFlush(dpy);
}

static void destroy_barriers(Display *dpy)
{
	for (int i = 0; i < barrier_count; i++)
		XFixesDestroyPointerBarrier(dpy, barrier[i]);

	barrier_count = 0;
	XFlush(dpy);
}
