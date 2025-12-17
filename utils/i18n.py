"""Internationalization (i18n) support for the application."""
import json
import locale
import os
from pathlib import Path
from typing import Dict, Optional

# Supported languages with their display names
SUPPORTED_LANGUAGES = {
    'ko': '한국어',
    'en': 'English',
    'ja': '日本語',
    'zh': '中文',
    'es': 'Español',
    'ru': 'Русский'
}

# Default fallback language
DEFAULT_LANGUAGE = 'en'


class I18n:
    """Internationalization manager for multi-language support."""

    _instance: Optional['I18n'] = None
    _translations: Dict[str, Dict[str, str]] = {}
    _current_language: str = DEFAULT_LANGUAGE
    _translations_dir: Path = Path(__file__).parent.parent / "locales"

    def __new__(cls):
        """Singleton pattern to ensure single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_all_translations()

    def _load_all_translations(self) -> None:
        """Load all translation files from locales directory."""
        if not self._translations_dir.exists():
            self._translations_dir.mkdir(parents=True, exist_ok=True)
            return

        for lang_code in SUPPORTED_LANGUAGES.keys():
            lang_file = self._translations_dir / f"{lang_code}.json"
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self._translations[lang_code] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Failed to load translation file {lang_file}: {e}")
                    self._translations[lang_code] = {}

    def get_system_language(self) -> str:
        """Detect system language and return matching supported language code."""
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Extract language code (e.g., 'ko_KR' -> 'ko')
                lang_code = system_locale.split('_')[0].lower()

                # Check if language is supported
                if lang_code in SUPPORTED_LANGUAGES:
                    return lang_code

                # Special case for Chinese variants
                if lang_code == 'zh':
                    return 'zh'
        except Exception:
            pass

        return DEFAULT_LANGUAGE

    def set_language(self, lang_code: str) -> bool:
        """Set the current language.

        Args:
            lang_code: Language code (e.g., 'ko', 'en', 'ja')

        Returns:
            True if language was set successfully, False otherwise
        """
        if lang_code in SUPPORTED_LANGUAGES:
            self._current_language = lang_code
            return True
        return False

    def get_language(self) -> str:
        """Get current language code."""
        return self._current_language

    def get_language_name(self, lang_code: Optional[str] = None) -> str:
        """Get display name for a language code."""
        code = lang_code or self._current_language
        return SUPPORTED_LANGUAGES.get(code, code)

    def t(self, key: str, **kwargs) -> str:
        """Translate a key to the current language.

        Args:
            key: Translation key
            **kwargs: Format arguments for string interpolation

        Returns:
            Translated string, or key if translation not found
        """
        # Try current language
        translation = self._translations.get(self._current_language, {}).get(key)

        # Fallback to default language
        if translation is None and self._current_language != DEFAULT_LANGUAGE:
            translation = self._translations.get(DEFAULT_LANGUAGE, {}).get(key)

        # Return key if no translation found
        if translation is None:
            return key

        # Apply format arguments if provided
        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError:
                return translation

        return translation

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages {code: display_name}."""
        return SUPPORTED_LANGUAGES.copy()

    def reload_translations(self) -> None:
        """Reload all translation files."""
        self._translations.clear()
        self._load_all_translations()


# Global instance for easy access
_i18n = I18n()


def get_system_language() -> str:
    """Get system language code."""
    return _i18n.get_system_language()


def set_language(lang_code: str) -> bool:
    """Set application language."""
    return _i18n.set_language(lang_code)


def get_language() -> str:
    """Get current language code."""
    return _i18n.get_language()


def t(key: str, **kwargs) -> str:
    """Translate a key to current language."""
    return _i18n.t(key, **kwargs)


def get_supported_languages() -> Dict[str, str]:
    """Get supported languages."""
    return _i18n.get_supported_languages()


def init_language(saved_language: Optional[str] = None) -> str:
    """Initialize language based on saved preference or system language.

    Args:
        saved_language: Previously saved language preference, or None/empty for auto-detect

    Returns:
        The language code that was set
    """
    if saved_language and saved_language in SUPPORTED_LANGUAGES:
        _i18n.set_language(saved_language)
        return saved_language
    else:
        # Auto-detect from system
        system_lang = _i18n.get_system_language()
        _i18n.set_language(system_lang)
        return system_lang
