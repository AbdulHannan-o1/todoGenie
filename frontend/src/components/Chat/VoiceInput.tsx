'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/src/components/ui/button';
import { Mic, MicOff, Loader2 } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (transcript: string) => void;
  disabled?: boolean;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, disabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef('');

  // Check browser support for Web Speech API
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (!SpeechRecognition) {
        setIsSupported(false);
        setError('Voice recognition is not supported in this browser.');
      }
    }
  }, []);

  const startListening = () => {
    if (!isSupported || disabled) return;

    try {
      setError(null);
      setIsProcessing(true);
      finalTranscriptRef.current = '';
      setTranscript('');

      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscriptRef.current += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }
        setTranscript(finalTranscriptRef.current + interimTranscript);
      };

      recognitionRef.current.onerror = (event: any) => {
        setError(`Speech recognition error: ${event.error}`);
        stopListening();
      };

      recognitionRef.current.onend = () => {
        if (isListening) {
          // If we stopped unexpectedly, try to restart
          startListening();
        }
      };

      recognitionRef.current.start();
      setIsListening(true);
      setIsProcessing(false);
    } catch (err) {
      setError('Failed to start voice recognition. Please check microphone permissions.');
      setIsProcessing(false);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);

    // Send final transcript if there's any
    if (finalTranscriptRef.current.trim()) {
      onTranscript(finalTranscriptRef.current.trim());
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!isSupported) {
    return (
      <div className="text-red-500 text-sm p-2">
        Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center space-y-2">
      <Button
        type="button"
        variant={isListening ? "destructive" : "default"}
        size="sm"
        onClick={toggleListening}
        disabled={disabled || isProcessing}
        className={`flex items-center gap-2 ${isListening ? 'animate-pulse' : ''}`}
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Processing...</span>
          </>
        ) : isListening ? (
          <>
            <div className="relative">
              <MicOff className="h-4 w-4" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-2 w-2 bg-red-500 rounded-full animate-ping"></div>
              </div>
            </div>
            <span>Stop Recording</span>
          </>
        ) : (
          <>
            <Mic className="h-4 w-4" />
            <span>Voice Input</span>
          </>
        )}
      </Button>

      {error && (
        <div className="text-red-500 text-sm p-2 bg-red-50 rounded-md w-full">
          {error}
        </div>
      )}

      {transcript && (
        <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded-md w-full">
          <p className="font-medium">Transcript:</p>
          <p>{transcript}</p>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;