import re
import hashlib
import httpx


async def pwned_api_check(password: str) -> int:
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Ошибка при запросе к API Pwned Passwords: {e}")
        return 0

    for line in response.text.splitlines():
        hash_suffix, count = line.split(':')
        if hash_suffix == suffix:
            return int(count)
    return 0


async def check_password_strength(password: str) -> str:
    pwned_count = await pwned_api_check(password)
    pwned_feedback = ""
    if pwned_count > 0:
        pwned_feedback = (
            f"🚨 *ВНИМАНИЕ!* 🚨\n"
            f"Этот пароль был найден `{pwned_count}` раз(а) в известных утечках данных. "
            f"**Ни в коем случае не используйте его!**\n\n"
            "------------------------------------\n"
        )

    length = len(password)
    has_digits = bool(re.search(r'\d', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_symbols = bool(re.search(r'[^a-zA-Z\d]', password))

    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if has_digits:
        score += 1
    if has_lower and has_upper:
        score += 1
    if has_symbols:
        score += 1

    if score <= 2:
        complexity_feedback = "🔴 Оценка сложности: Очень слабый"
    elif score == 3:
        complexity_feedback = "🟠 Оценка сложности: Средний"
    elif score == 4:
        complexity_feedback = "🟡 Оценка сложности: Хороший"
    else:
        complexity_feedback = "🟢 Оценка сложности: Очень сильный"

    details = []
    if length < 8:
        details.append("• Увеличьте длину до 8+ символов")
    if not has_lower or not has_upper:
        details.append("• Используйте буквы разного регистра (a-z, A-Z)")
    if not has_digits:
        details.append("• Добавьте цифры (0-9)")
    if not has_symbols:
        details.append("• Добавьте спецсимволы (!@#$%)")

    recommendations = ""
    if details:
        recommendations = "\n\n*Рекомендации по улучшению:*\n" + \
            "\n".join(details)

    final_feedback = pwned_feedback + complexity_feedback + recommendations
    return final_feedback
