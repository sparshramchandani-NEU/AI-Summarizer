import React, { useState, useEffect } from 'react';

// Common languages with their codes
const LANGUAGES = [
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

// Dictionary-based translations for demonstration purposes
// In production, you would use a proper translation service
const TRANSLATIONS = {
  'es': {  // Spanish
    'summary': 'resumen',
    'hello': 'hola',
    'world': 'mundo',
    'welcome': 'bienvenido',
    'thank you': 'gracias'
  },
  'fr': {  // French
    'summary': 'résumé',
    'hello': 'bonjour',
    'world': 'monde',
    'welcome': 'bienvenue',
    'thank you': 'merci'
  },
  'de': {  // German
    'summary': 'zusammenfassung',
    'hello': 'hallo',
    'world': 'welt',
    'welcome': 'willkommen',
    'thank you': 'danke'
  }
};

const TalkingAvatar = ({ text, autoPlay = false, apiUrl }) => {
  const [speaking, setSpeaking] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [filteredVoices, setFilteredVoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [translating, setTranslating] = useState(false);
  const [translatedText, setTranslatedText] = useState('');
  const [error, setError] = useState(null);

  // Load and filter available voices
  useEffect(() => {
    function loadVoices() {
      const availableVoices = window.speechSynthesis.getVoices();
      if (availableVoices.length > 0) {
        setVoices(availableVoices);
        setLoading(false);
        
        // Filter voices by selected language
        filterVoicesByLanguage(availableVoices, selectedLanguage);
      }
    }
    
    loadVoices();
    
    // Chrome loads voices asynchronously
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      // Clean up
      if (speaking) {
        window.speechSynthesis.cancel();
      }
    };
  }, [speaking]);
  
  // When text changes, reset translation
  useEffect(() => {
    setTranslatedText('');
  }, [text]);
  
  // Filter voices when language changes
  useEffect(() => {
    filterVoicesByLanguage(voices, selectedLanguage);
    // Reset translated text when language changes
    setTranslatedText('');
  }, [selectedLanguage, voices]);
  
  const filterVoicesByLanguage = (allVoices, langCode) => {
    // Get the base language code (e.g., 'en' from 'en-US')
    const baseLangCode = langCode.split('-')[0].toLowerCase();
    
    // Filter voices by language code - more flexible to match partial codes
    const matchingVoices = allVoices.filter(voice => 
      voice.lang.toLowerCase().includes(baseLangCode)
    );
    
    setFilteredVoices(matchingVoices);
    
    // Select the first matching voice or keep the current one if it matches
    if (matchingVoices.length > 0) {
      if (!selectedVoice || !matchingVoices.some(v => v.name === selectedVoice.name)) {
        setSelectedVoice(matchingVoices[0]);
      }
    } else {
      // If no matching voices, reset to null
      setSelectedVoice(null);
    }
  };

  // Translate text to selected language
  const translateText = async (targetLanguage) => {
    setTranslating(true);
    setError(null);
    
    try {
      // Get the language code without the region specifier
      const langCode = targetLanguage.split('-')[0];
      
      // Don't translate if the selected language is English
      if (langCode === 'en') {
        setTranslatedText(text);
        setTranslating(false);
        return;
      }
      
      // SIMPLE DICTIONARY-BASED TRANSLATION (FALLBACK APPROACH)
      // This is a simple fallback that doesn't rely on external APIs
      // It just demonstrates the concept - in production you would use a real translation service
      if (TRANSLATIONS[langCode]) {
        let result = text;
        
        // Simple word replacement
        Object.entries(TRANSLATIONS[langCode]).forEach(([english, translated]) => {
          const regex = new RegExp('\\b' + english + '\\b', 'gi');
          result = result.replace(regex, translated);
        });
        
        // For demo purposes, prefix the text to show translation was attempted
        result = `[${langCode}] ${result}`;
        
        setTranslatedText(result);
        setTranslating(false);
        return;
      }
      
      // Try server API translation if dictionary doesn't have the language
      console.log(`Attempting API translation to ${langCode}...`);
      
      // First try with your API
      try {
        const response = await fetch(`${apiUrl}translate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: text,
            target_language: langCode
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.translated_text) {
            setTranslatedText(data.translated_text);
            setTranslating(false);
            return;
          }
        }
      } catch (apiError) {
        console.error("API translation error:", apiError);
        // Continue to fallback
      }
      
      // If API fails, fall back to original text with language tag
      const fallbackText = `[${langCode}] ${text}`;
      setTranslatedText(fallbackText);
      
    } catch (error) {
      console.error('Translation error:', error);
      setError('Translation failed. Using original text.');
      // Fallback to original text if translation fails
      setTranslatedText(text);
    } finally {
      setTranslating(false);
    }
  };

  // Handle speak button click
  const handleSpeak = async () => {
    if (speaking) {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      setSpeaking(false);
      return;
    }
    
    if (!window.speechSynthesis) {
      alert("Your browser doesn't support text-to-speech. Please try another browser.");
      return;
    }
    
    // Translate text if not already translated
    if (!translatedText) {
      await translateText(selectedLanguage);
    }
    
    // Start speaking
    setSpeaking(true);
    
    // Create and configure utterance
    const utterance = new SpeechSynthesisUtterance(translatedText || text);
    
    // Set language and voice if available
    utterance.lang = selectedLanguage;
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    // Set speech parameters
    utterance.rate = 1.0;
    utterance.pitch = 1.1;
    
    // Add event handlers
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setSpeaking(false);
    };
    
    // Speak the text
    window.speechSynthesis.speak(utterance);
  };

  // Handle language change
  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setSelectedLanguage(newLanguage);
    // Clear the translated text to force new translation
    setTranslatedText('');
  };

  return (
    <div className="avatar-container">
      <div className="avatar-display">
        <div className="avatar-placeholder">
          <img 
            src="https://api.dicebear.com/7.x/personas/svg?seed=talking" 
            alt="Avatar" 
            className={speaking ? 'avatar-speaking' : ''}
          />
        </div>
      </div>
      
      <div className="avatar-controls">
        {/* Language selection */}
        <div className="language-selection">
          <label htmlFor="language-select">Language:</label>
          <select 
            id="language-select"
            value={selectedLanguage}
            onChange={handleLanguageChange}
            disabled={speaking}
            className="language-select"
          >
            {LANGUAGES.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
        
        {/* Voice selection */}
        <div className="voice-selection">
          <label htmlFor="voice-select">Voice:</label>
          <select 
            id="voice-select"
            value={selectedVoice ? selectedVoice.name : ''}
            onChange={(e) => {
              const voice = voices.find(v => v.name === e.target.value);
              setSelectedVoice(voice);
            }}
            disabled={filteredVoices.length === 0 || speaking}
            className="voice-select"
          >
            {filteredVoices.length > 0 ? (
              filteredVoices.map(voice => (
                <option key={voice.name} value={voice.name}>
                  {voice.name}
                </option>
              ))
            ) : (
              <option value="">No voices available for this language</option>
            )}
          </select>
        </div>
        
        {/* Translation status */}
        {translating && (
          <div className="translation-status">
            Translating text to {LANGUAGES.find(l => l.code === selectedLanguage)?.name}...
          </div>
        )}
        
        {/* Error message */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {/* Show translation preview */}
        {translatedText && selectedLanguage !== 'en-US' && (
          <div className="translation-preview">
            <strong>Translation:</strong>
            <div>{translatedText}</div>
          </div>
        )}
        
        {/* Speak button */}
        <button 
          onClick={handleSpeak}
          className={`avatar-speak-button ${speaking ? 'speaking' : ''}`}
          disabled={loading || filteredVoices.length === 0 || translating || !text}
        >
          {loading ? (
            <span><i className="fas fa-spinner fa-spin"></i> Loading voices...</span>
          ) : translating ? (
            <span><i className="fas fa-spinner fa-spin"></i> Translating...</span>
          ) : speaking ? (
            <span><i className="fas fa-stop"></i> Stop Speaking</span>
          ) : (
            <span><i className="fas fa-play"></i> Speak in {LANGUAGES.find(l => l.code === selectedLanguage)?.name}</span>
          )}
        </button>
      </div>
    </div>
  );
};

export default TalkingAvatar;