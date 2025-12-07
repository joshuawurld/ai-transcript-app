export type RecordingState = 'idle' | 'recording' | 'processing';

export interface AppState {
  isRecording: boolean;
  isProcessing: boolean;
  rawText: string | null;
  cleanedText: string | null;
  isCleaningWithLLM: boolean;
  error: string | null;
  useLLM: boolean;
  isCopied: boolean;
  systemPrompt: string;
  isLoadingPrompt: boolean;
  isDragging: boolean;
}

export interface TranscriptionResponse {
  text: string;
}

export interface CleanTextResponse {
  cleaned_text: string;
}

export interface SystemPromptResponse {
  default_prompt: string;
}

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface HeaderProps {}

export interface RecordButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  onStartRecording: () => Promise<void>;
  onStopRecording: () => void;
}

export interface UploadZoneProps {
  isProcessing: boolean;
  isDragging: boolean;
  onFileSelect: (file: File) => void;
  onDragEnter: () => void;
  onDragLeave: () => void;
  onDrop: (file: File) => void;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
}

export interface TextInputZoneProps {
  isProcessing: boolean;
  onTextSubmit: (text: string) => Promise<void>;
}

export interface SettingsPanelProps {
  useLLM: boolean;
  systemPrompt: string;
  isLoadingPrompt: boolean;
  onToggleLLM: (value: boolean) => void;
  onPromptChange: (value: string) => void;
}

export interface TranscriptionResultsProps {
  rawText: string | null;
  cleanedText: string | null;
  useLLM: boolean;
  isCopied: boolean;
  isCleaningWithLLM: boolean;
  isProcessing: boolean;
  isOriginalExpanded: boolean;
  onCopy: (text: string) => void;
  onToggleOriginalExpanded: () => void;
}

export interface ErrorMessageProps {
  message: string;
  onDismiss: () => void;
}

export interface TextBoxProps {
  value: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  mode: 'input' | 'display';
  variant?: 'default' | 'enhanced';
  isLoading?: boolean;
  isDisabled?: boolean;
  showCopyButton?: boolean;
  isCopied?: boolean;
  onCopy?: () => void;
  rows?: number;
  maxHeight?: string;
  ariaLabel?: string;
  id?: string;
}

export interface BoxProps {
  children: React.ReactNode;
  header?: string;
  icon?: React.ComponentType<{ className?: string }>;
  collapsible?: boolean;
  isExpanded?: boolean;
  onToggleExpanded?: () => void;
  className?: string;
}

export type AudioFileType =
  | 'audio/mpeg'
  | 'audio/wav'
  | 'audio/webm'
  | 'audio/ogg'
  | 'audio/x-m4a';

export const ACCEPTED_AUDIO_TYPES: AudioFileType[] = [
  'audio/mpeg',
  'audio/wav',
  'audio/webm',
  'audio/ogg',
  'audio/x-m4a',
];
