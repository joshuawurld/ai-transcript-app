import { Upload } from 'lucide-react';
import styles from './UploadZone.module.css';
import type { UploadZoneProps } from '../types';

export function UploadZone({
  isProcessing,
  isDragging,
  onFileSelect,
  onDragEnter,
  onDragLeave,
  onDrop,
  fileInputRef,
}: UploadZoneProps) {
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    onDragEnter();
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    onDragLeave();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    onDragLeave();

    const files = e.dataTransfer.files;
    if (files && files.length > 0 && files[0]) {
      onDrop(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0 && files[0]) {
      void onFileSelect(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const zoneClass = `${styles.zone} ${isDragging ? styles.dragging : ''} ${isProcessing ? styles.processing : ''}`;

  return (
    <div className={styles.container}>
      <div className={styles.divider}>
        <span>OR</span>
      </div>

      <div
        className={zoneClass}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleClick();
          }
        }}
        aria-label="Upload audio file"
      >
        <Upload className={styles.icon} />
        <p className={styles.title}>
          {isDragging ? 'Drop file here' : 'Upload Audio File'}
        </p>
        <p className={styles.subtitle}>Drag and drop or click to browse</p>
        <p className={styles.formats}>MP3, WAV, M4A, WebM, OGG</p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleFileInputChange}
        className={styles.hiddenInput}
        aria-hidden="true"
      />
    </div>
  );
}
