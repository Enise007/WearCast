from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, jsonify
from src.utils.auth import register_user, login_user, delete_user_profile, update_user_profile
from src.utils.auth import delete_user_account_permanently
import os
import jwt
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

blp = Blueprint("Auth", __name__, description="User Auth Operations")

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

@blp.route("/register")
class Register(MethodView):
    def post(self):
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        birthdate = data["birthdate"]
        gender = data["gender"]
        city = "Not Mentioned"

        user = register_user(email, password)

        if isinstance(user, dict) and "error" in user:
            return jsonify({"error": user["error"]}), 400
        if hasattr(user, 'user') and getattr(user, 'user', None) is not None:
            user_id = user.user.id
            supabase.table("user_profiles").insert({
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                'email': email,
                "birthdate": birthdate,
                "gender": gender,
                "city": city
            }).execute()
            
            try:
                login_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if hasattr(login_response, 'session') and login_response.session:
                    access_token = login_response.session.access_token
                    return jsonify({
                        "message": "Kayıt başarılı ve otomatik giriş yapıldı", 
                        "user_id": user_id,
                        "access_token": access_token
                    })
                else:
                    return jsonify({
                        "message": "Kayıt başarılı - lütfen giriş yapın", 
                        "user_id": user_id,
                        "email": email,
                        "auto_login_failed": True
                    })
            except Exception as e:
                print(f"Otomatik giriş hatası: {e}")
                return jsonify({
                    "message": "Kayıt başarılı - lütfen giriş yapın", 
                    "user_id": user_id,
                    "email": email,
                    "auto_login_failed": True
                })
        else:
            return jsonify({"error": "Kullanıcı kaydı başarısız."}), 400
    
@blp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    print(">>> [DEBUG] login_user çağrıldı")
    print(">>> E-posta:", email)

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        user = getattr(response, 'user', None)
        session = getattr(response, 'session', None)
        if user is None or session is None:
            return jsonify({"error": "Giriş başarısız. Hatalı e-posta veya şifre."}), 400
        print(">>> Supabase yanıtı:", response)
        access_token = getattr(session, 'access_token', None)
        user_id = getattr(user, 'id', None)
        return jsonify({"access_token": access_token, "user_id": user_id}), 200

    except Exception as e:
        print(">>> [HATA] Giriş yaparken exception:", str(e))
        return jsonify({"error": "Giriş başarısız. Hatalı e-posta veya şifre."}), 400

@blp.route("/me")
class Me(MethodView):
    def patch(self):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid token"}), 401

            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                return jsonify({"error": "Invalid token"}), 401

            updates = request.get_json() or {}
            result = update_user_profile(user_id, updates)

            if "error" in result:
                return jsonify({"error": result["error"]}), 400

            return jsonify({"message": "Profil güncellendi", "profile": result["data"]}), 200

        except Exception as e:
            print(f"[HATA] /me PATCH: {e}")
            return jsonify({"error": "An error occurred while updating profile"}), 500

    def delete(self):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid token"}), 401

            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                return jsonify({"error": "Invalid token"}), 401

            result = delete_user_account_permanently(user_id)

            if "error" in result:
                if "bulunamadı" in result["error"]:
                    return jsonify({"error": result["error"]}), 404
                return jsonify({"error": result["error"]}), 400

            return "", 204

        except Exception as e:
            print(f"[HATA] /me DELETE: {e}")
            return jsonify({"error": "An error occurred while deleting profile"}), 500

    def get(self):
        try:
            auth_header =request.headers.get("Authorization")
            auth_header =request.headers.get("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1] 
            else:
                return jsonify({"error": "Missing or invalid token"}), 401


            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")


            if not user_id:
                return {"error": "Invalid token"}, 401
            
            response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            user_data = response.data
            
            if not user_data:
                return {"error": "User not found"}, 401
            
            return jsonify(user_data[0])
        
        except Exception as e:
            print(f"[HATA] /me endpoint: {e}")
            return {"error": "An error occurred while fetching user info"}, 500

@blp.route("/prompt")
class Prompt(MethodView):
    def post(self):
        try:

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid token"}), 401
            
            token = auth_header.split(" ")[1]

            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")


            response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            user_data = response.data

            if not user_data:
                return jsonify({"error": "User not found"}), 401
            
            user_info = user_data[0]
            first_name = user_info["first_name"]
            last_name = user_info["last_name"]
            birthdate = user_info.get("birthdate")
            email = user_info["email"]
            gender = user_info["gender"]
            city = user_info["city"]

            weather_data = "Sıcaklık 30°C, nem %60, güneşli"

            prompt = f"""
                Kullanıcı bilgileri:
                - İsim: {first_name} {last_name}
                - Doğum Tarihi: {birthdate}
                - Cinsiyet: {gender}
                - Şehir: {city}

                Bu bilgilere göre kullanıcıya özel öneriler üret:
                {weather_data}
                """
            return jsonify({
                "prompt": prompt
            })
        
        except Exception as e:
            print(f"[Hata] /prompt endpoint: {e}")
            return jsonify({"error": "An error occurred"}), 500
        
@blp.route('/chat_history')
class ChatHistory(MethodView):
    def get(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                return jsonify({"error": "Invalid token"}), 401
            response = supabase.table("conversation_history") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=False) \
                .execute()
            return jsonify({"history": response.data})
        except Exception as e:
            print("[HATA] chat_history:", e)
            return jsonify({"error": "An error occurred while fetching chat history"}), 500


from src.utils.auth import (
    register_user, login_user, delete_user_profile, update_user_profile,
    verify_user_password, admin_update_user_email, admin_update_user_password
)
def _get_user_id_from_request():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, ("Missing or invalid token", 401)
    token = auth_header.split(" ")[1]
    decoded = jwt.decode(token, options={"verify_signature": False})
    user_id = decoded.get("sub")
    if not user_id:
        return None, ("Invalid token", 401)
    return user_id, None


@blp.route("/me/email")
class MeEmail(MethodView):
    def patch(self):
        try:
            user_id, err = _get_user_id_from_request()
            if err: return jsonify({"error": err[0]}), err[1]

            body = request.get_json() or {}
            new_email = body.get("new_email")
            password = body.get("password")
            if not new_email:
                return jsonify({"error": "new_email is required"}), 400
            if not password:
                return jsonify({"error": "password is required"}), 400

            prof = supabase.table("user_profiles").select("email").eq("id", user_id).single().execute()
            current_email = (prof.data or {}).get("email")
            if not current_email:
                return jsonify({"error": "User not found"}), 404

            if not verify_user_password(current_email, password):
                return jsonify({"error": "Current password is wrong"}), 403

            admin_update_user_email(user_id, new_email)

            supabase.table("user_profiles").update({"email": new_email}).eq("id", user_id).execute()

            return jsonify({"message": "Email updated", "email": new_email}), 200
        except Exception as e:
            print("[HATA] /me/email:", e)
            return jsonify({"error": "An error occurred while updating email"}), 500


@blp.route("/me/password")
class MePassword(MethodView):
    def patch(self):
        try:
            user_id, err = _get_user_id_from_request()
            if err: return jsonify({"error": err[0]}), err[1]

            body = request.get_json() or {}
            current_password = body.get("current_password")
            new_password = body.get("new_password")
            if not current_password or not new_password:
                return jsonify({"error": "current_password and new_password are required"}), 400

            prof = supabase.table("user_profiles").select("email").eq("id", user_id).single().execute()
            email = (prof.data or {}).get("email")
            if not email:
                return jsonify({"error": "User not found"}), 404

            if not verify_user_password(email, current_password):
                return jsonify({"error": "Current password is wrong"}), 403

            admin_update_user_password(user_id, new_password)

            return jsonify({"message": "Password updated"}), 200
        except Exception as e:
            print("[HATA] /me/password:", e)
            return jsonify({"error": "An error occurred while updating password"}), 500
