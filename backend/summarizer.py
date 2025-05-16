"""
Enhanced TensorFlow-based Text Summarization model with multiple summarization styles
"""
import tensorflow as tf
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer
import numpy as np

class EnhancedTFSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """
        Initialize the summarization model with TensorFlow backend
        
        Args:
            model_name (str): Name of the Hugging Face model to use
        """
        self.model_name = model_name
        print(f"Loading model: {model_name}")
        
        # Load model and tokenizer with TensorFlow backend
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Check if GPU is available
        self.gpu_available = len(tf.config.list_physical_devices('GPU')) > 0
        if self.gpu_available:
            print("GPU is available for inference")
        else:
            print("Running on CPU")
            
        # Define summarization styles
        self.styles = {
            "default": {
                "description": "Balanced summary with key information",
                "params": {
                    "num_beams": 4,
                    "no_repeat_ngram_size": 3,
                    "length_penalty": 1.0,
                    "early_stopping": True
                }
            },
            "concise": {
                "description": "Very brief summary focusing only on the most critical points",
                "params": {
                    "num_beams": 5,
                    "no_repeat_ngram_size": 3,
                    "length_penalty": 0.6,  # Prefer shorter outputs
                    "early_stopping": True
                }
            },
            "detailed": {
                "description": "Comprehensive summary covering more information",
                "params": {
                    "num_beams": 5,
                    "no_repeat_ngram_size": 2,
                    "length_penalty": 2.0,  # Increased to favor longer outputs
                    "early_stopping": False,
                    "min_length_factor": 0.2,  # 20% of original text length
                    "max_length_factor": 0.4   # 40% of original text length
                }
            },
            "very_detailed": {
                "description": "Highly comprehensive summary with extensive details",
                "params": {
                    "num_beams": 6,
                    "no_repeat_ngram_size": 2,
                    "length_penalty": 3.0,     # Strong preference for longer outputs
                    "temperature": 0.7,        # Slightly more creative generation
                    "early_stopping": False,
                    "min_length_factor": 0.3,  # 30% of original text length
                    "max_length_factor": 0.5   # 50% of original text length
                }
            },
            "aggressive": {
                "description": "Highly abstractive summary that condenses information significantly",
                "params": {
                    "num_beams": 6,
                    "no_repeat_ngram_size": 4,
                    "length_penalty": 0.4,  # Strongly prefer shorter outputs
                    "early_stopping": True
                }
            },
            "creative": {
                "description": "More paraphrased and creatively reworded summary",
                "params": {
                    "num_beams": 5,
                    "temperature": 1.2,  # More diversity in generation
                    "top_k": 50,
                    "top_p": 0.9,
                    "no_repeat_ngram_size": 2,
                    "length_penalty": 1.0,
                    "early_stopping": True
                }
            },
            "bullets": {
                "description": "Summary formatted as bullet points",
                "params": {
                    "num_beams": 4,
                    "no_repeat_ngram_size": 3,
                    "length_penalty": 1.0,
                    "early_stopping": True,
                    "prefix": "Key points:\n• ",
                    "format_bullets": True
                }
            },
            "eli5": {
                "description": "Explain Like I'm 5 - Summary in simple language",
                "params": {
                    "num_beams": 4,
                    "no_repeat_ngram_size": 2,
                    "length_penalty": 1.0,
                    "prefix": "In simple terms: ",
                    "early_stopping": True
                }
            },
            "academic": {
                "description": "Formal academic style summary",
                "params": {
                    "num_beams": 5,
                    "no_repeat_ngram_size": 2,
                    "length_penalty": 1.2,
                    "early_stopping": True
                }
            }
        }
        
    def get_available_styles(self):
        """
        Get all available summarization styles
        
        Returns:
            dict: Dictionary of style names and descriptions
        """
        return {name: style["description"] for name, style in self.styles.items()}
        
    def summarize(self, text, max_length=150, min_length=30, style="default"):
        """
        Summarize the provided text using the specified style
        
        Args:
            text (str): The text to summarize
            max_length (int): Maximum summary length
            min_length (int): Minimum summary length
            style (str): Summarization style to use
            
        Returns:
            dict: Summary information
        """
        # Get style configuration
        if style not in self.styles:
            print(f"Style '{style}' not found, using default style")
            style = "default"
            
        style_config = self.styles[style]
        style_params = style_config["params"].copy()
        
        # Calculate dynamic lengths based on input size if factors are provided
        text_length = len(text.split())
        if "min_length_factor" in style_params:
            min_length_factor = style_params.pop("min_length_factor")
            min_length = max(min_length, int(text_length * min_length_factor))
        
        if "max_length_factor" in style_params:
            max_length_factor = style_params.pop("max_length_factor")
            max_length = max(max_length, int(text_length * max_length_factor))
        
        # Ensure max_length is at least min_length
        max_length = max(max_length, min_length)
        
        # Extract special parameters
        prefix = style_params.pop("prefix", "")
        format_bullets = style_params.pop("format_bullets", False)
        
        # Control abstractiveness if specified
        if "abstractiveness" in style_params:
            abstractiveness = style_params.pop("abstractiveness")
            # Use different parameters based on abstractiveness
            if abstractiveness > 0.7:
                style_params["temperature"] = 0.8  # Higher temperature = more creative
                style_params["top_p"] = 0.9        # Nucleus sampling
            else:
                style_params["temperature"] = 0.2  # Lower temperature = more focused
                style_params["top_p"] = 0.6        # More conservative sampling
        
        # For long texts, we need to chunk them
        if len(text.split()) > 1024:  # Most models have a limit of ~1024 tokens
            text = self._truncate_text(text, 1024)
            
        # Prepare input text
        if prefix:
            # Let the model start with the prefix
            prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
            
        # Tokenize the input
        inputs = self.tokenizer(text, return_tensors="tf", max_length=1024, truncation=True)
        
        # Generate summary with style-specific parameters
        summary_ids = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            min_length=min_length,
            **style_params
        )
        
        # Decode the generated tokens
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        # Apply post-processing based on style
        if prefix and not summary.startswith(prefix):
            summary = prefix + summary
            
        if format_bullets:
            summary = self._format_as_bullets(summary)
            
        if style == "academic" and not any(word in summary.lower() for word in ["research", "study", "analysis", "therefore", "consequently"]):
            # Add some academic flair if it's not already present
            if "." in summary:
                parts = summary.split(".")
                parts[-2] = parts[-2] + ", therefore"
                summary = ".".join(parts)
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "style": style,
            "style_description": style_config["description"]
        }
    
    def summarize_long_document(self, text, max_length=300, min_length=100, style="detailed"):
        """
        Summarize a long document by breaking it into segments, summarizing each,
        and then combining and summarizing the results.
        
        Args:
            text (str): The text to summarize
            max_length (int): Maximum summary length
            min_length (int): Minimum summary length
            style (str): Summarization style to use
            
        Returns:
            dict: Summary information
        """
        # Split document into segments (e.g., paragraphs or sections)
        segments = self._split_into_segments(text)
        
        # Summarize each segment
        segment_summaries = []
        for segment in segments:
            if len(segment.split()) > 50:  # Only summarize substantial segments
                summary = self.summarize(segment, max_length=150, min_length=30, style=style)
                segment_summaries.append(summary["summary"])
        
        # Combine segment summaries
        combined_summary = " ".join(segment_summaries)
        
        # Create a meta-summary of the combined summaries
        if len(combined_summary.split()) > max_length:
            final_summary = self.summarize(
                combined_summary, 
                max_length=max_length, 
                min_length=min_length, 
                style="default"  # Use default style for final summary
            )
            return final_summary
        else:
            return {
                "summary": combined_summary,
                "original_length": len(text),
                "summary_length": len(combined_summary),
                "style": style,
                "style_description": self.styles[style]["description"]
            }
    
    def _truncate_text(self, text, max_tokens):
        """
        Truncate text to max_tokens (approximate implementation)
        """
        words = text.split()
        if len(words) <= max_tokens:
            return text
        return " ".join(words[:max_tokens])
    
    def _split_into_segments(self, text, max_segment_tokens=800):
        """
        Split text into meaningful segments (paragraphs or sections)
        """
        # Simple paragraph-based splitting
        paragraphs = text.split('\n\n')
        
        segments = []
        current_segment = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            if current_length + para_length <= max_segment_tokens:
                current_segment.append(para)
                current_length += para_length
            else:
                if current_segment:
                    segments.append(' '.join(current_segment))
                current_segment = [para]
                current_length = para_length
        
        # Add the last segment
        if current_segment:
            segments.append(' '.join(current_segment))
        
        return segments
        
    def _format_as_bullets(self, text):
        """
        Format text as bullet points
        """
        if "• " not in text:
            # If the model didn't generate bullet points, create them
            sentences = text.split('. ')
            if len(sentences) <= 1:
                return text
                
            # Remove any existing prefix
            if sentences[0].startswith("Key points:"):
                sentences.pop(0)
                
            # Format as bullet points
            bullet_text = "Key points:\n"
            for sentence in sentences:
                if sentence and not sentence.isspace():
                    # Clean up the sentence
                    sentence = sentence.strip()
                    if not sentence.endswith('.'):
                        sentence += '.'
                    bullet_text += f"• {sentence}\n"
                    
            return bullet_text.strip()
        else:
            # The model already generated bullet points
            return text