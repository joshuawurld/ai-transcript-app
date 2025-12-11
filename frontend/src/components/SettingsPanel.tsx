import { Sparkles, ChevronDown, ChevronUp, Settings, GitBranch } from 'lucide-react';
import styles from './SettingsPanel.module.css';
import { useState } from 'react';
import { TextBox } from './TextBox';
import { Box } from './Box';

interface Props {
  useLLM: boolean;
  useAgent: boolean;
  systemPrompt: string;
  isLoadingPrompt: boolean;
  onToggleLLM: (value: boolean) => void;
  onToggleAgent: (value: boolean) => void;
  onPromptChange: (value: string) => void;
}

export function SettingsPanel({
  useLLM,
  useAgent,
  systemPrompt,
  isLoadingPrompt,
  onToggleLLM,
  onToggleAgent,
  onPromptChange,
}: Props) {
  const [isPromptExpanded, setIsPromptExpanded] = useState(false);
  const [isReviewingIssues, setIsReviewingIssues] = useState(false);
  const [reviewStarted, setReviewStarted] = useState(false);

  const handleReviewIssues = async () => {
    setIsReviewingIssues(true);
    setReviewStarted(true);

    try {
      await fetch('/api/review-issues', {
        method: 'POST',
      });
    } catch {
      // Errors will be visible in terminal
    } finally {
      setIsReviewingIssues(false);
    }
  };

  return (
    <Box header="Settings" icon={Settings}>
      {/* Agent Processing Toggle */}
      <div className={styles.toggleSection}>
        <label className={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={useAgent}
            onChange={(e) => onToggleAgent(e.target.checked)}
            className={styles.checkbox}
          />
          <Sparkles className={styles.toggleIcon} />
          <span className={styles.toggleText}>
            Process with AI Agent
          </span>
        </label>
        <p className={styles.description}>
          Agent analyzes transcripts and creates calendar reminders with meeting summaries, action items, blockers, and urgent issues
        </p>
      </div>

      {/* Simple LLM Cleaning Toggle */}
      <div className={styles.toggleSection}>
        <label className={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={useLLM}
            onChange={(e) => onToggleLLM(e.target.checked)}
            className={styles.checkbox}
          />
          <span className={styles.toggleText}>
            Clean text with LLM (optional)
          </span>
        </label>
        <p className={styles.description}>
          Simple text cleaning: remove filler words, fix grammar
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

      {/* GitHub Issue Review - MCP Demo */}
      <div className={styles.issueReviewSection}>
        <div className={styles.issueReviewHeader}>
          <GitBranch className={styles.toggleIcon} />
          <span className={styles.issueReviewTitle}>GitHub Issue Review</span>
          <span className={styles.mcpBadge}>MCP</span>
        </div>
        <p className={styles.description}>
          Autonomous agent that discovers and reviews issues via MCP
        </p>
        <button
          className={styles.reviewButton}
          onClick={() => void handleReviewIssues()}
          disabled={isReviewingIssues}
          type="button"
        >
          {isReviewingIssues ? 'Agent Running...' : 'Start Issue Review Agent'}
        </button>

        {reviewStarted && (
          <p className={styles.terminalNote}>
            See terminal for agent output
          </p>
        )}
      </div>
    </Box>
  );
}
