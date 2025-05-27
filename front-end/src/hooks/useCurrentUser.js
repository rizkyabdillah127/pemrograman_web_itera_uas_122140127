import Cookies from "js-cookie";

export function useCurrentUser() {
  const userCookie = Cookies.get("user");
  const authTkt = Cookies.get("auth_tkt");

  // Keduanya harus tersedia agar user dianggap terautentikasi
  if (!userCookie || !authTkt) return null;

  try {
    return JSON.parse(userCookie);
  } catch (e) {
    console.error("Invalid user cookie format");
    return null;
  }
}
