import React from 'react';

// Enhanced message formatter utility for better text display
export const formatMessage = (content) => {
  if (!content || typeof content !== 'string') {
    return content;
  }

  // First, let's handle the content more intelligently
  // Split by periods followed by numbers (for numbered lists) or double line breaks
  let sections = [];
  let currentSection = '';
  
  // Split content into logical sections
  const lines = content.split('\n');
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Check if this is a numbered list item
    if (line.match(/^\d+\.\s\*\*/)) {
      if (currentSection.trim()) {
        sections.push(currentSection.trim());
        currentSection = '';
      }
      sections.push(line);
    }
    // Check if this is a bullet point
    else if (line.match(/^-\s\*\*/)) {
      sections.push(line);
    }
    // Regular content
    else {
      currentSection += (currentSection ? '\n' : '') + line;
    }
  }
  
  // Add remaining content
  if (currentSection.trim()) {
    sections.push(currentSection.trim());
  }
  
  return sections.map((section, index) => {
    if (!section || section.trim() === '') return null;
    
    // Handle code blocks
    if (section.startsWith('```')) {
      const codeContent = section.replace(/^```[\w]*\n?/, '').replace(/\n?```$/, '');
      return (
        <pre key={index} style={{
          background: 'rgba(0, 0, 0, 0.4)',
          padding: '16px',
          borderRadius: '8px',
          overflow: 'auto',
          fontSize: '14px',
          fontFamily: 'Consolas, "Courier New", monospace',
          margin: '12px 0',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
        }}>
          <code style={{ color: '#e6db74' }}>{codeContent}</code>
        </pre>
      );
    }
    
    // Handle numbered main points (like "1. **Title:**")
    if (section.match(/^\d+\.\s\*\*/)) {
      const formattedSection = section
        .replace(/(\d+\.\s)\*\*(.*?)\*\*(:?)/g, '<div class="numbered-header"><span class="number">$1</span><strong class="title">$2</strong>$3</div>')
        .replace(/\n/g, '<br />');
      
      return (
        <div key={index} style={{
          background: 'linear-gradient(135deg, rgba(74, 144, 226, 0.1), rgba(80, 200, 120, 0.1))',
          padding: '16px 20px',
          borderRadius: '12px',
          margin: '16px 0',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          position: 'relative'
        }}>
          <div 
            dangerouslySetInnerHTML={{ __html: formattedSection }}
            style={{ 
              fontSize: '16px',
              lineHeight: '1.8',
              color: '#ffffff'
            }}
          />
          <style jsx>{`
            .numbered-header {
              display: flex;
              align-items: center;
              margin-bottom: 8px;
            }
            .number {
              background: linear-gradient(135deg, #4a90e2, #50c878);
              color: white;
              padding: 6px 12px;
              border-radius: 20px;
              font-weight: bold;
              margin-right: 12px;
              font-size: 14px;
              min-width: 40px;
              text-align: center;
            }
            .title {
              color: #4a90e2;
              font-size: 18px;
              text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            }
          `}</style>
        </div>
      );
    }
    
    // Handle bullet points with bold headers (like "- **Title:** content")
    if (section.match(/^-\s\*\*/)) {
      const formattedSection = section
        .replace(/^-\s\*\*(.*?)\*\*(:?)\s*(.*)/, '<div class="bullet-item"><span class="bullet">•</span><strong class="bullet-title">$1</strong>$2 <span class="bullet-content">$3</span></div>');
      
      return (
        <div key={index} style={{
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '12px 16px',
          borderRadius: '8px',
          margin: '8px 0 8px 20px',
          borderLeft: '4px solid #4a90e2',
          boxShadow: '0 2px 6px rgba(0, 0, 0, 0.15)'
        }}>
          <div 
            dangerouslySetInnerHTML={{ __html: formattedSection }}
            style={{ 
              fontSize: '15px',
              lineHeight: '1.7',
              color: '#ffffff'
            }}
          />
          <style jsx>{`
            .bullet-item {
              display: flex;
              align-items: flex-start;
            }
            .bullet {
              color: #4a90e2;
              font-size: 18px;
              margin-right: 10px;
              margin-top: 2px;
            }
            .bullet-title {
              color: #50c878;
              margin-right: 8px;
            }
            .bullet-content {
              color: #e0e0e0;
              flex: 1;
            }
          `}</style>
        </div>
      );
    }
    
    
    // Handle regular paragraphs with enhanced formatting
    const formattedParagraph = section
      .replace(/\*\*(.*?)\*\*/g, '<strong style="color: #4a90e2; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">$1</strong>') // Bold with blue color
      .replace(/\*(.*?)\*/g, '<em style="color: #50c878;">$1</em>') // Italic with green color
      .replace(/`(.*?)`/g, '<code style="background: rgba(0, 0, 0, 0.3); padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; color: #e6db74;">$1</code>') // Inline code
      .replace(/\n/g, '<br />'); // Line breaks
    
    return (
      <div 
        key={index}
        style={{
          background: 'rgba(255, 255, 255, 0.03)',
          padding: '14px 18px',
          borderRadius: '10px',
          margin: '10px 0',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          lineHeight: '1.8',
          fontSize: '15px',
          color: '#e8e8e8',
          textAlign: 'justify',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}
        dangerouslySetInnerHTML={{ __html: formattedParagraph }}
      />
    );
  }).filter(Boolean);
};

// Enhanced Message Component with better styling
export const FormattedMessage = ({ content, role }) => {
  const formattedContent = formatMessage(content);
  
  return (
    <div className={`message ${role}`}>
      <div className="message-content" style={{
        background: role === 'assistant' 
          ? 'linear-gradient(135deg, rgba(74, 144, 226, 0.15), rgba(80, 200, 120, 0.15))'
          : 'linear-gradient(135deg, rgba(128, 90, 213, 0.15), rgba(255, 159, 90, 0.15))',
        padding: '20px',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        backdropFilter: 'blur(10px)',
        maxWidth: '100%',
        wordWrap: 'break-word',
        fontSize: '15px',
        lineHeight: '1.7'
      }}>
        {Array.isArray(formattedContent) ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {formattedContent}
          </div>
        ) : (
          <div style={{ color: '#e8e8e8' }}>{content}</div>
        )}
      </div>
    </div>
  );
};
