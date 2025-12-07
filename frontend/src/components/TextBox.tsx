import { Copy, Check } from 'lucide-react';
import styles from './TextBox.module.css';
import { Spinner } from './Spinner';
import type { TextBoxProps } from '../types';

export function TextBox({
  value,
  onChange,
  placeholder,
  mode,
  variant: _variant = 'default',
  isLoading = false,
  isDisabled = false,
  showCopyButton = false,
  isCopied = false,
  onCopy,
  rows = 6,
  maxHeight,
  ariaLabel,
  id,
}: TextBoxProps) {
  const containerClasses = [
    styles.textBox,
    styles[mode],
    isLoading && styles.loading,
  ]
    .filter(Boolean)
    .join(' ');

  const handleCopy = () => {
    if (onCopy && value) {
      onCopy();
    }
  };

  return (
    <div className={styles.wrapper}>
      <div className={containerClasses} style={{ maxHeight }}>
        {isLoading ? (
          <Spinner />
        ) : mode === 'input' ? (
          <textarea
            id={id}
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            placeholder={placeholder}
            disabled={isDisabled}
            rows={rows}
            aria-label={ariaLabel}
            className={styles.textarea}
          />
        ) : (
          <p className={styles.text}>{value}</p>
        )}
      </div>

      {showCopyButton && !isLoading && value && (
        <button
          onClick={handleCopy}
          className={styles.copyButton}
          aria-label={isCopied ? 'Copied to clipboard' : 'Copy to clipboard'}
        >
          {isCopied ? (
            <>
              <Check className={styles.icon} />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy className={styles.icon} />
              <span>Copy</span>
            </>
          )}
        </button>
      )}
    </div>
  );
}
