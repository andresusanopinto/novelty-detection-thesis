#include <string>
#include <sstream>

template<class T>
std::string to_string(const T a) {
  std::ostringstream os;
  os << a;
  return os.str();
}

