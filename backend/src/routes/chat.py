from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify, request
import datetime
import jwt
import uuid
from supabase import create_client
from src.core.engine import tool_call, create_response
from flask import jsonify, request
import re
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

blp = Blueprint('Chat', __name__, description='Chat Operations')


def _clean_generated_title(raw_title):
    if not raw_title:
        return "New Chat"

    first_line = next((ln.strip() for ln in raw_title.splitlines() if ln.strip()), "").strip()

    cleaned = first_line
    cleaned = cleaned.strip('`"\' ')
    cleaned = re.sub(r"^[#>*\-•\s]+", "", cleaned)
    cleaned = re.sub(r"^\s*\d+[\).-]\s*", "", cleaned)

    cleaned = re.sub(r"[\u2190-\u21FF\u2600-\u27BF\U0001F300-\U0001FAD6]+", "", cleaned)
    cleaned = cleaned.strip(" -–—:;,.!?")

    if not cleaned:
        cleaned = "New Chat"

    if len(cleaned) > 60:
        cleaned = cleaned[:57].rstrip() + "…"

    return cleaned


def build_conversation_title(user_message):
    title_prompt = f"""
        Generate exactly one concise, descriptive conversation title for the user's first message below.

        Requirements:
        - Language: Use the same language as the user's message.
        - Length: 3–8 words, maximum 60 characters.
        - Style: No quotes, no emojis, no markdown. For English use Title Case; for Turkish, capitalize only the first word and proper nouns.
        - Content: Capture the main intent/topic; include important entities like city, event, product, or weather context if present.
        - Avoid: Generic words like Chat, Conversation, Question, Hello.

        User message:
        {user_message}

        Return only the title text.
    """.strip()

    raw = create_response(title_prompt)
    return _clean_generated_title(raw)

@blp.route('/chat')
class Chat(MethodView):
    def post(self):
        data = request.get_json()
        user_prompt = data.get('prompt')
        conversation_id = data.get('conversation_id')

        if not user_prompt:
            abort(400, message="Prompt is required")

        user_profile = None
        user_id = None
        title_response = None

        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                abort(401, message="Missing or invalid Authorization header")

            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")

            if not user_id:
                abort(401, message="Invalid token: User ID not found")

            profile_response = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()

            if profile_response.data:
                user_profile = profile_response.data
                computed_age = None
                try:
                    birthdate_value = user_profile.get('birthdate')
                    if birthdate_value:
                        from datetime import date
                        b = date.fromisoformat(str(birthdate_value)[:10])
                        today = date.today()
                        computed_age = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
                except Exception:
                    computed_age = None
                print(
                    f"User profile found: {user_profile['first_name']} (Age: {computed_age}, Gender: {user_profile['gender']})")
            else:
                print(f"Warning: User profile not found in database for user_id: {user_id}")

        except Exception as e:
            print(f"Auth or Profile error, continuing without profile: {e}")

        history_context = ""
        if user_id and conversation_id:
            try:
                history_resp = supabase.table("conversation_history") \
                    .select("role, message") \
                    .eq("conversation_id", conversation_id) \
                    .order("created_at", desc=False) \
                    .limit(6) \
                    .execute()

                if history_resp.data:
                    history_messages = []
                    for item in history_resp.data:
                        role_name = "Kullanıcı" if item['role'] == 'user' else "Asistan"
                        history_messages.append(f"{role_name}: {item['message']}")

                    history_context = "Önceki Konuşma Bağlamı:\n" + "\n".join(history_messages) + "\n\n---\n\n"
                    print("Sohbet geçmişi bağlamı oluşturuldu.")

            except Exception as e:
                print(f"[UYARI] Sohbet geçmişi alınamadı: {e}")

        if user_profile and not conversation_id:
            title_response = build_conversation_title(user_prompt)
            conversation_id = str(uuid.uuid4())
            supabase.table("conversations").insert({
                "id": conversation_id,
                "user_id": user_id,
                "title": title_response,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).execute()

        rules_prompt = """
            1- You MUST respond in the same language as the user's question! If they ask in Turkish, respond in Turkish. If they ask in English, respond in English. If they ask in Spanish, respond in Spanish, and so on.
            2- Do not greet the user.
            3- Do not ask the user for their location.
            4- Do not act like you are given information act as you know it.
            5- Use **Markdown formatting** to make your response more readable (e.g., **bold** for emphasis, bullet points for lists).
            6- Use emojis in the response.
        """

        base_prompt = tool_call(user_prompt)

        final_prompt = ""
        if not user_profile:
            final_prompt = history_context + rules_prompt + base_prompt + f"\n\nUser Question:\n{user_prompt}"
        else:
            user_profile_prompt = f"""
                User profile:
                User name: {user_profile['first_name']} 
                Age: {computed_age}
                Gender: {user_profile['gender']}
                City: {user_profile['city']}
                If question can be leveraged from user profile, use it.
                Use users name in the response.
            """
            final_prompt = history_context + rules_prompt + user_profile_prompt + base_prompt + f"\n\nUser Question:\n{user_prompt}"

        response = create_response(final_prompt)

        if user_profile and conversation_id:
            try:
                supabase.table("conversation_history").insert([
                    {"user_id": user_id, "role": "user", "message": user_prompt, "conversation_id": conversation_id,
                     "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                ]).execute()
                supabase.table("conversation_history").insert([
                    {"user_id": user_id, "role": "assistant", "message": response, "conversation_id": conversation_id,
                     "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
                ]).execute()
            except Exception as e:
                print(f"Supabase conversation insert error: {e}")

        if user_profile and conversation_id:
            return jsonify({
                "response": response,
                "conversation_id": conversation_id,
                "title": title_response if 'title_response' in locals() else None
            })
        else:
            return jsonify({"response": response})


@blp.route('/conversations')
class Conversations(MethodView):
    def get(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                abort(401, message="Invalid token: User ID not found")
        except Exception as e:
            abort(401, message="Invalid token")

        try:
            resp = supabase.table("conversations").select("id, title, created_at").eq("user_id", user_id).order(
                "created_at", desc=True).execute()
            conversations = resp.data if resp.data else []
        except Exception as e:
            print(f"[ERROR] Supabase fetch conversations: {e}")
            conversations = []
        return jsonify({"conversations": conversations})
    
    def delete(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                abort(401, message="Invalid token: User ID not found")
        except Exception:
            abort(401, message="Invalid token")

        try:
            supabase.table("conversation_history").delete().eq("user_id", user_id).execute()
            supabase.table("conversations").delete().eq("user_id", user_id).execute()
            return jsonify({"message": "All conversations deleted"}), 200
        except Exception as e:
            print(f"[ERROR] Supabase delete all conversations: {e}")
            abort(500, message="Failed to delete conversations")


@blp.route('/conversations/<conversation_id>/history')
class ConversationHistory(MethodView):
    def get(self, conversation_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                abort(401, message="Invalid token: User ID not found")
        except Exception as e:
            abort(401, message="Invalid token")

        try:
            resp = supabase.table("conversation_history").select("*").eq("conversation_id", conversation_id).eq(
                "user_id", user_id).order("created_at", desc=False).execute()
            history = resp.data if resp.data else []
            conv_resp = supabase.table("conversations").select("title").eq("id", conversation_id).eq("user_id",
                                                                                                     user_id).single().execute()
            conversation_title = conv_resp.data.get("title") if conv_resp.data else None

            return jsonify({
                "conversation_id": conversation_id,
                "title": conversation_title,
                "history": history
            })
        except Exception as e:
            print(f"[ERROR] Supabase fetch conversation history: {e}")
            abort(500, message="Failed to fetch conversation history")  


@blp.route('/conversations/<conversation_id>')
class ConversationResource(MethodView):
    def patch(self, conversation_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                abort(401, message="Invalid token: User ID not found")
        except Exception:
            abort(401, message="Invalid token")

        data = request.get_json() or {}
        new_title = data.get("title")
        if new_title is None:
            abort(400, message="Missing 'title' in request body")

        conv_resp = supabase.table("conversations").select("id").eq("id", conversation_id).eq("user_id", user_id).single().execute()
        if not conv_resp.data:
            abort(404, message="Conversation not found")

        cleaned_title = _clean_generated_title(str(new_title))
        try:
            supabase.table("conversations").update({"title": cleaned_title}).eq("id", conversation_id).eq("user_id", user_id).execute()
            return jsonify({"message": "Conversation updated", "id": conversation_id, "title": cleaned_title}), 200
        except Exception as e:
            print(f"[ERROR] Supabase update conversation title: {e}")
            abort(500, message="Failed to update conversation")

    def delete(self, conversation_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            if not user_id:
                abort(401, message="Invalid token: User ID not found")
        except Exception:
            abort(401, message="Invalid token")

        try:
            conv_resp = supabase.table("conversations").select("id").eq("id", conversation_id).eq("user_id", user_id).single().execute()
            if not conv_resp.data:
                abort(404, message="Conversation not found")

            supabase.table("conversation_history").delete().eq("conversation_id", conversation_id).eq("user_id", user_id).execute()
            supabase.table("conversations").delete().eq("id", conversation_id).eq("user_id", user_id).execute()
            return jsonify({"message": "Conversation deleted", "conversation_id": conversation_id}), 200
        except Exception as e:
            print(f"[ERROR] Supabase delete conversation: {e}")
            abort(500, message="Failed to delete conversation")