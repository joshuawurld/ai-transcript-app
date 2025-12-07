import { Sparkles, ChevronDown, ChevronUp, Settings } from 'lucide-react';
import styles from './SettingsPanel.module.css';
import type { SettingsPanelProps } from '../types';
import { useState } from 'react';
import { TextBox } from './TextBox';
import { Box } from './Box';

export function SettingsPanel({
  useLLM,
  systemPrompt,
  isLoadingPrompt,
  onToggleLLM,
  onPromptChange,
}: SettingsPanelProps) {
  const [isPromptExpanded, setIsPromptExpanded] = useState(false);

  return (
    <Box header="Settings" icon={Settings}>
      {/* Main LLM Toggle - Always Visible */}
      <div className={styles.toggleSection}>
        <label className={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={useLLM}
            onChange={(e) => onToggleLLM(e.target.checked)}
            className={styles.checkbox}
          />
          <Sparkles className={styles.toggleIcon} />
          <span className={styles.toggleText}>
            Clean transcription with LLM
          </span>
        </label>
        <p className={styles.description}>
          Use AI to clean up transcription (remove filler words, fix grammar)
        </p>
      </div>

      {/* System Prompt - Collapsible Advanced Option */}
      {useLLM && (
        <div className={styles.promptSection}>
          <button
            className={styles.promptHeader}
            onClick={() => setIsPromptExpanded(!isPromptExpanded)}
            aria-expanded={isPromptExpanded}
            aria-label={
              isPromptExpanded
                ? 'Collapse system prompt'
                : 'Expand system prompt'
            }
            type="button"
          >
            <span className={styles.promptLabel}>System Prompt</span>
            {isPromptExpanded ? (
              <ChevronUp className={styles.chevron} />
            ) : (
              <ChevronDown className={styles.chevron} />
            )}
          </button>

          {isPromptExpanded && (
            <div className={styles.promptContent}>
              <TextBox
                mode="input"
                variant="default"
                value={systemPrompt}
                onChange={onPromptChange}
                placeholder="Enter system prompt for LLM..."
                isLoading={isLoadingPrompt}
                rows={6}
                id="systemPrompt"
              />
            </div>
          )}
        </div>
      )}
    </Box>
  );
}
