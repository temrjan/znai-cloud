/**
 * Box component - styled div with sx prop support
 * Replacement for @primer/react Box
 */
import { CSSProperties, forwardRef } from 'react';

interface BoxProps extends React.HTMLAttributes<any> {
  as?: keyof JSX.IntrinsicElements;
  sx?: Record<string, any>;
  children?: React.ReactNode;
  [key: string]: any; // Allow any additional props
}

export const Box = forwardRef<any, BoxProps>(
  ({ as = 'div', sx = {}, children, style, ...props }, ref) => {
    const Component = as as any;

    // Convert sx object to inline styles
    const combinedStyle: CSSProperties = {
      ...convertSxToStyle(sx),
      ...style,
    };

    return (
      <Component ref={ref} style={combinedStyle} {...props}>
        {children}
      </Component>
    );
  }
);

Box.displayName = 'Box';

// Helper function to convert sx object to CSSProperties
function convertSxToStyle(sx: Record<string, any>): CSSProperties {
  const style: any = {};

  Object.entries(sx).forEach(([key, value]) => {
    // Skip pseudo-classes and nested selectors
    if (key.startsWith('&') || key.startsWith('@')) {
      return;
    }

    style[key] = value;
  });

  return style as CSSProperties;
}
