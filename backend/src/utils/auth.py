from supabase import create_client
import os
from flask import jsonify

from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY =os.getenv("SUPABASE_API_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)
admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def register_user(email, password):
    print(">>> [DEBUG] register_user çağrıldı")
    print(">>> E-posta:", email)
    try:
        response =supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        print(">>> Supabase yanıtı:", response)
        return response
    except Exception as e:
        print(">>> [HATA] Kayıt olurken exception:", str(e))
        return {"error": str(e)}

def login_user(email, password):
    print(">>> [DEBUG] login_user çağrıldı")
    print(">>> E-posta:", email)
    try:
        response=supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        print(">>> Supabase yanıtı:", response)
        return response
    except Exception as e:
        print(">>> [HATA] Giriş yaparken exception:", str(e))
        return {"error": str(e)}

ALLOWED_PROFILE_FIELDS = {"first_name", "last_name", "email", "birthdate", "city", "gender"}

def update_user_profile(user_id: str, updates: dict):
    if not user_id:
        return {"error": "Kullanıcı bulunamadı."}

    if not isinstance(updates, dict):
        return {"error": "Geçersiz güncelleme verisi."}

    payload = {k: v for k, v in updates.items() if k in ALLOWED_PROFILE_FIELDS}
    if not payload:
        return {"error": "Güncellenecek geçerli bir alan bulunamadı."}

    try:
        resp = supabase.table("user_profiles").update(payload).eq("id", user_id).execute()
        if not getattr(resp, "data", None):
            return {"error": "Güncelleme başarısız veya kayıt bulunamadı."}
        return {"data": resp.data[0]}
    except Exception as e:
        return {"error": f"Güncelleme sırasında hata: {e}"}

def delete_user_account_permanently(user_id: str):
    if not user_id:
        return {"error": "Kullanıcı ID'si sağlanmadı."}
    try:
        admin_supabase.auth.admin.delete_user(user_id)
        return {"data": True, "message": "Kullanıcı kalıcı olarak silindi."}
    except Exception as e:
        print(f"[HATA] Kalıcı kullanıcı silme hatası: {e}")
        error_message = str(e)
        if "User not found" in error_message:
            return {"error": "Silinecek kullanıcı bulunamadı."}
        return {"error": f"Kullanıcı silinirken bir hata oluştu: {error_message}"}
def delete_user_profile(user_id: str):
    if not user_id:
        return {"error": "Kullanıcı bulunamadı."}

    try:
        resp = supabase.table("user_profiles").delete().eq("id", user_id).execute()
        return {"data": True}
    except Exception as e:
        return {"error": f"Silme sırasında hata: {e}"}

def verify_user_password(email: str, password: str) -> bool:
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return getattr(resp, "user", None) is not None and getattr(resp, "session", None) is not None
    except Exception:
        return False

def admin_update_user_email(user_id: str, new_email: str):
    return admin_supabase.auth.admin.update_user_by_id(user_id, {"email": new_email})

def admin_update_user_password(user_id: str, new_password: str):
    return admin_supabase.auth.admin.update_user_by_id(user_id, {"password": new_password})