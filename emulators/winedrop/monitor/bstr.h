#ifndef H_BSTR
#define H_BSTR

#include <stdlib.h>

extern unsigned int BStr_byte_length(wchar_t* bstr);
extern unsigned int BStr_length(wchar_t* bstr);
extern wchar_t* BStr_new(wchar_t* wc, unsigned int len);
extern wchar_t* BStr_copy(wchar_t* bstr);
extern wchar_t* BStr_free(wchar_t* bstr);
extern unsigned int CBStr_hash(wchar_t* bstr);

#endif