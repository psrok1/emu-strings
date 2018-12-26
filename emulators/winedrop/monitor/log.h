#ifndef H_LOG
#define H_LOG

extern void log_init();
extern void log_send_raw(const char* data, unsigned int length);
extern void log_send(char type, const char* fmt, ...);

#endif