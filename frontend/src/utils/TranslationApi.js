// utils/TranslationApi.js

/**
 * API client for the translation functionality
 */

/**
 * Translates text to the specified language
 * 
 * @param {string} text - The text to translate
 * @param {string} targetLanguage - The language code to translate to
 * @param {string} apiUrl - The base URL for the API
 * @returns {Promise<Object>} - Promise containing the translation result
 */
export const translateText = async (text, targetLanguage, apiUrl) => {
    try {
      // Get the language code without the region specifier (e.g., 'en' from 'en-US')
      const langCode = targetLanguage.split('-')[0];
      
      // Don't translate if the target language is English
      if (langCode === 'en') {
        return {
          translated_text: text,
          source_language: 'en',
          target_language: langCode
        };
      }
      
      // API call to translate
      const response = await fetch(`${apiUrl}translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          target_language: langCode
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Translation failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Translation API error:', error);
      throw error;
    }
  };
  
  /**
   * Get available translation languages
   * 
   * @returns {Promise<Array>} - Promise containing available languages
   */
  export const getAvailableLanguages = async () => {
    try {
      // In a real implementation, you would fetch this from the API
      // For now, we'll return a static list that matches our frontend
      return [
        { code: 'en-US', name: 'English (US)' },
        { code: 'es-ES', name: 'Spanish' },
        { code: 'fr-FR', name: 'French' },
        { code: 'de-DE', name: 'German' },
        { code: 'it-IT', name: 'Italian' },
        { code: 'pt-BR', name: 'Portuguese' },
        { code: 'ru-RU', name: 'Russian' },
        { code: 'zh-CN', name: 'Chinese' },
        { code: 'ja-JP', name: 'Japanese' },
        { code: 'ko-KR', name: 'Korean' },
        { code: 'ar-SA', name: 'Arabic' },
        { code: 'hi-IN', name: 'Hindi' },
        { code: 'nl-NL', name: 'Dutch' },
        { code: 'pl-PL', name: 'Polish' },
        { code: 'sv-SE', name: 'Swedish' },
        { code: 'tr-TR', name: 'Turkish' }
      ];
    } catch (error) {
      console.error('Error fetching available languages:', error);
      throw error;
    }
  };
  
  /**
   * Check if translation API is available and functioning
   * 
   * @param {string} apiUrl - The base URL for the API
   * @returns {Promise<boolean>} - Promise containing API status
   */
  export const checkTranslationApiStatus = async (apiUrl) => {
    try {
      const response = await fetch(`${apiUrl}health`);
      return response.ok;
    } catch (error) {
      console.error('Translation API health check failed:', error);
      return false;
    }
  };