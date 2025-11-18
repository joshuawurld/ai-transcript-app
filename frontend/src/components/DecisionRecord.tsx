import { useState } from 'react';
import { Copy, Check, Lightbulb } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { DecisionRecordProps } from '../types';
import styles from './DecisionRecord.module.css';

export function DecisionRecord({ markdownContent, data }: DecisionRecordProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(markdownContent);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const getStatusClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'accepted':
        return styles.statusAccepted;
      case 'proposed':
        return styles.statusProposed;
      case 'rejected':
        return styles.statusRejected;
      case 'deprecated':
        return styles.statusDeprecated;
      case 'superseded':
        return styles.statusSuperseded;
      default:
        return styles.statusProposed;
    }
  };

  return (
    <div className={styles.container}>
      {/* Header with status and copy button */}
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <Lightbulb className={styles.icon} />
          <h3 className={styles.title}>Decision Record (ADR)</h3>
        </div>
        <div className={styles.actions}>
          <span className={`${styles.statusBadge} ${getStatusClass(data.status)}`}>
            {data.status.toUpperCase()}
          </span>
          <button
            onClick={handleCopy}
            className={styles.copyButton}
            title={isCopied ? 'Copied!' : 'Copy decision record to clipboard'}
          >
            {isCopied ? <Check size={16} /> : <Copy size={16} />}
            {isCopied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>

      {/* Decision info summary */}
      <div className={styles.infoSection}>
        <div className={styles.infoGrid}>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Decision:</span>
            <span className={styles.infoValue}>{data.decision_title}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Date:</span>
            <span className={styles.infoValue}>{data.decision_date}</span>
          </div>
          {data.decision_makers && data.decision_makers.length > 0 && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Decision Makers:</span>
              <span className={styles.infoValue}>{data.decision_makers.join(', ')}</span>
            </div>
          )}
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Options Evaluated:</span>
            <span className={styles.infoValue}>{data.options_considered.length}</span>
          </div>
        </div>
      </div>

      {/* Full decision record */}
      <div className={styles.recordSection}>
        <details className={styles.details} open>
          <summary className={styles.detailsSummary}>
            Full Decision Record
          </summary>
          <div className={styles.recordContent}>
            <div className={styles.markdown}>
              <ReactMarkdown>{markdownContent}</ReactMarkdown>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}
