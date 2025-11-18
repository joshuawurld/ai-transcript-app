import { FileText, Sparkles } from 'lucide-react';
import styles from './TranscriptionResults.module.css';
import type { TranscriptionResultsProps } from '../types';
import { TextBox } from './TextBox';
import { Box } from './Box';

export function TranscriptionResults({
  rawText,
  cleanedText,
  useLLM,
  isCopied,
  isCleaningWithLLM,
  isProcessing,
  isOriginalExpanded,
  onCopy,
  onToggleOriginalExpanded,
}: TranscriptionResultsProps) {
  // Show component if either processing or rawText exists
  if (!isProcessing && !rawText) {
    return null;
  }

  return (
    <div className={styles.container}>
      <Box
        header="Original Transcription"
        icon={FileText}
        collapsible={true}
        isExpanded={isOriginalExpanded}
        onToggleExpanded={onToggleOriginalExpanded}
      >
        <TextBox
          mode="display"
          variant="default"
          value={rawText || ''}
          isLoading={isProcessing && !rawText}
          showCopyButton={!useLLM && !!rawText}
          isCopied={isCopied}
          onCopy={() => rawText && onCopy(rawText)}
          maxHeight="300px"
        />
      </Box>

      {/* Cleaned transcription (if LLM is enabled and cleaned text exists or is processing) */}
      {useLLM && (cleanedText || isCleaningWithLLM) && (
        <Box header="Cleaned Transcription" icon={Sparkles}>
          <TextBox
            mode="display"
            variant="default"
            value={cleanedText || ''}
            isLoading={isCleaningWithLLM}
            showCopyButton={!!cleanedText}
            isCopied={isCopied}
            onCopy={() => cleanedText && onCopy(cleanedText)}
            maxHeight="300px"
          />
        </Box>
      )}
    </div>
  );
}
