#ifndef H_LOG
#define H_LOG

extern void log_init();
extern void log_send(const char* channel, const char* fmt, ...);

#endif