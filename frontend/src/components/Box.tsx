import { ChevronDown, ChevronUp } from 'lucide-react';
import styles from './Box.module.css';
import type { BoxProps } from '../types';

export function Box({
  children,
  header,
  icon: Icon,
  collapsible = false,
  isExpanded = true,
  onToggleExpanded,
  className,
}: BoxProps) {
  return (
    <div className={`${styles.box} ${className || ''}`}>
      {header && (
        <div className={styles.header}>
          {collapsible ? (
            <button
              className={styles.collapsibleHeader}
              onClick={onToggleExpanded}
              aria-expanded={isExpanded}
              aria-label={
                isExpanded ? `Collapse ${header}` : `Expand ${header}`
              }
              type="button"
            >
              {Icon && <Icon className={styles.icon} />}
              <h3 className={styles.title}>{header}</h3>
              {isExpanded ? (
                <ChevronUp className={styles.chevron} />
              ) : (
                <ChevronDown className={styles.chevron} />
              )}
            </button>
          ) : (
            <>
              {Icon && <Icon className={styles.icon} />}
              <h3 className={styles.title}>{header}</h3>
            </>
          )}
        </div>
      )}
      {(!collapsible || isExpanded) && (
        <div className={styles.content}>{children}</div>
      )}
    </div>
  );
}
