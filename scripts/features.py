# -*- coding: utf-8 -*-
"""
Feature extraction for Persian sentence style scoring.
"""
from __future__ import annotations
import re
from typing import Dict, List


# ---------------------------------------------------------------------------
# Vocabulary groups
# ---------------------------------------------------------------------------
# These lists are research features, not complete Persian lexicons.
COLLOQUIAL_WORDS = {
    "خیلی", "یه", "یهو", "اصلا", "واقعا", "الان", "خب", "حالا", "بابا", "آدم", "حوصله", "دلم",
    "میخوام", "نمیخوام", "نمیشه", "میشه", "اگه", "چیکار", "کلا", "خوبه", "بدجور"
}
BROKEN_WORDS = {
    "میخوام", "نمیخوام", "نمیشه", "میشه", "اگه", "چیکار", "واسه", "برا", "دارم", "ندارم", "میگم"
}
FORMAL_WORDS = {
    "خواهشمند", "مربوطه", "مقتضی", "ارسال", "فرمایید", "بدینوسیله", "موارد", "مذکور", "اقدام", "بررسی",
    "لازم", "محترم", "جنابعالی", "پیوست", "مطابق", "ضروری", "ارائه", "نتیجه", "مستلزم", "فرآیند"
}
ACADEMIC_WORDS = {
    "تحلیل", "پژوهش", "مدل", "داده", "ویژگی", "ساختار", "زبان", "معیار", "ارزیابی", "نتایج",
    "فرضیه", "روش", "چارچوب", "طبقه‌بندی", "یادگیری", "معنادار", "کاربرد", "پیاده‌سازی"
}
LITERARY_WORDS = {
    "اندوه", "جان", "دل", "غبار", "آینه", "رغبت", "خاموش", "سایه", "سپیده", "شب", "روشنایی",
    "زبان", "جهان", "تنهایی", "آرام", "دریغ", "آرزو", "خاطر", "روح", "باران", "کوچه", "خاکستر",
    "آسمان", "تاریکی", "روشنی", "فروغ", "غم", "سکوت", "نفس", "دریا", "بامداد", "فرجام"
}
CLASSICAL_WORDS = {
    "چون", "زان", "کز", "بدان", "بدین", "همی", "گشت", "آمدی", "بماند", "رخ", "دیده", "دلبر",
    "خویش", "جهان", "نیک", "بد", "فرخنده", "چرخ", "فلک", "سپهر", "جانان"
}
LITERARY_PHRASES = [
    "بر جان", "آینه دل", "غبار اندوه", "در جانم", "سایه غم", "زبانم از سخن", "دست و دلم",
    "خانه کرده", "بر دلم", "بر آینه", "دل از جهان", "در آغوش", "خاکستر خاطره"
]
ARABIC_FORMAL_SUFFIXES = ("ات", "یت", "انه", "مند", "گونه", "سازی", "پذیر", "مندی")


# ---------------------------------------------------------------------------
# Text normalization and tokenization
# ---------------------------------------------------------------------------
PERSIAN_LETTER_RE = re.compile(r"[آ-ی]+")


def normalize(text: str) -> str:
    text = str(text or "")
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = text.replace("\u200c", "‌")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    text = normalize(text)
    return PERSIAN_LETTER_RE.findall(text)


def count_set(tokens: List[str], vocab: set) -> int:
    return sum(1 for t in tokens if t in vocab)


# ---------------------------------------------------------------------------
# Numeric feature extraction
# ---------------------------------------------------------------------------
def extract_features(text: str) -> Dict[str, float]:
    text = normalize(text)
    tokens = tokenize(text)
    word_count = len(tokens)
    char_count = len(text)
    avg_word_length = round(sum(len(t) for t in tokens) / word_count, 3) if word_count else 0.0
    long_word_count = sum(1 for t in tokens if len(t) >= 7)

    lower_text = text
    literary_phrase_count = sum(1 for p in LITERARY_PHRASES if p in lower_text)
    arabic_formal_suffix_count = sum(1 for t in tokens if t.endswith(ARABIC_FORMAL_SUFFIXES) and len(t) > 4)

    return {
        "word_count": float(word_count),
        "char_count": float(char_count),
        "avg_word_length": float(avg_word_length),
        "long_word_count": float(long_word_count),
        "colloquial_count": float(count_set(tokens, COLLOQUIAL_WORDS)),
        "broken_word_count": float(count_set(tokens, BROKEN_WORDS)),
        "formal_count": float(count_set(tokens, FORMAL_WORDS)),
        "academic_count": float(count_set(tokens, ACADEMIC_WORDS)),
        "literary_count": float(count_set(tokens, LITERARY_WORDS)),
        "classical_count": float(count_set(tokens, CLASSICAL_WORDS)),
        "literary_phrase_count": float(literary_phrase_count),
        "arabic_formal_suffix_count": float(arabic_formal_suffix_count),
        "comma_count": float(text.count("،") + text.count(",")),
        "semicolon_count": float(text.count("؛") + text.count(";")),
        "question_mark_count": float(text.count("؟") + text.count("?")),
        "exclamation_count": float(text.count("!") + text.count("!")),
    }

FEATURE_KEYS = list(extract_features("نمونه جمله ساده فارسی.").keys())


# ---------------------------------------------------------------------------
# Human-readable labels and explanations
# ---------------------------------------------------------------------------
def score_label(score: int) -> str:
    score = int(round(score))
    if score <= 2:
        return "محاوره‌ای و روزمره"
    if score <= 4:
        return "ساده و معیار"
    if score <= 6:
        return "رسمی / نیمه‌کتابی"
    if score <= 8:
        return "ادبی و فاخر"
    return "بسیار ادبی / شاعرانه"


def factor_summary(features: Dict[str, float]) -> List[str]:
    items: List[str] = []
    if features.get("colloquial_count", 0) or features.get("broken_word_count", 0):
        items.append("وجود واژه‌های محاوره‌ای یا شکسته، امتیاز ادبی را پایین‌تر می‌آورد.")
    if features.get("formal_count", 0):
        items.append("وجود واژه‌های رسمی باعث افزایش لحن کتابی و اداری شده است.")
    if features.get("academic_count", 0):
        items.append("واژه‌های علمی/پژوهشی باعث رسمی‌تر شدن جمله شده‌اند.")
    if features.get("literary_count", 0):
        items.append("واژه‌های عاطفی و ادبی باعث افزایش امتیاز ادبی شده‌اند.")
    if features.get("classical_count", 0):
        items.append("واژه‌های کلاسیک، جمله را کهن‌تر و فاخرتر نشان می‌دهند.")
    if features.get("literary_phrase_count", 0):
        items.append("ترکیب‌های تصویری یا ادبی، نقش مهمی در بالا رفتن امتیاز دارند.")
    if features.get("word_count", 0) >= 14:
        items.append("طول جمله نسبتا زیاد است و می‌تواند نشانه ساختار رسمی‌تر یا پیچیده‌تر باشد.")
    if not items:
        items.append("جمله از نظر واژگان شاخص، ساده و کم‌نشانه است؛ امتیاز بیشتر به الگوی کلی جمله وابسته بوده است.")
    return items


def simple_explanation(score: int, features: Dict[str, float]) -> str:
    label = score_label(score)
    reasons = factor_summary(features)[:2]
    return f"این جمله در گروه «{label}» قرار گرفته است. " + " ".join(reasons)
