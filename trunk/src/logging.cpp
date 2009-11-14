#include "base/logging.h"

namespace logging {

LogMessage::LogMessage(const char* file, int line, LogSeverity severity, int ctr)
{

}

LogMessage::LogMessage(const char* file, int line)
{

}

LogMessage::LogMessage(const char* file, int line, LogSeverity severity)
{

}

LogMessage::LogMessage(const char* file, int line, const CheckOpString& result)
{

}

LogMessage::~LogMessage()
{

}

void LogMessage::Init(const char* file, int line)
{
}

}