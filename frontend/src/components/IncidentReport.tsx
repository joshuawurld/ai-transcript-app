import { useState } from 'react';
import { Copy, Check, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { IncidentReportProps } from '../types';
import styles from './IncidentReport.module.css';

export function IncidentReport({ markdownContent, data }: IncidentReportProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(markdownContent);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const getSeverityClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return styles.severityCritical;
      case 'high':
        return styles.severityHigh;
      case 'medium':
        return styles.severityMedium;
      case 'low':
        return styles.severityLow;
      default:
        return styles.severityMedium;
    }
  };

  return (
    <div className={styles.container}>
      {/* Header with severity and copy button */}
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <AlertTriangle className={styles.icon} />
          <h3 className={styles.title}>Incident Report</h3>
        </div>
        <div className={styles.actions}>
          <span className={`${styles.severityBadge} ${getSeverityClass(data.severity)}`}>
            {data.severity.toUpperCase()}
          </span>
          <button
            onClick={handleCopy}
            className={styles.copyButton}
            title={isCopied ? 'Copied!' : 'Copy report to clipboard'}
          >
            {isCopied ? <Check size={16} /> : <Copy size={16} />}
            {isCopied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>

      {/* Incident info summary */}
      <div className={styles.infoSection}>
        <div className={styles.infoGrid}>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Incident:</span>
            <span className={styles.infoValue}>{data.incident_title}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Started:</span>
            <span className={styles.infoValue}>{data.start_time}</span>
          </div>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Resolved:</span>
            <span className={styles.infoValue}>{data.resolution_time || 'Ongoing'}</span>
          </div>
          {data.business_impact?.downtime_duration && (
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Downtime:</span>
              <span className={styles.infoValue}>{data.business_impact.downtime_duration}</span>
            </div>
          )}
        </div>
      </div>

      {/* Full report text */}
      <div className={styles.reportSection}>
        <details className={styles.details} open>
          <summary className={styles.detailsSummary}>
            Full Report
          </summary>
          <div className={styles.reportContent}>
            <div className={styles.markdown}>
              <ReactMarkdown>{markdownContent}</ReactMarkdown>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}
