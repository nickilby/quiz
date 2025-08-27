# QuizzNight Brand Guide

## Brand Overview

QuizzNight is a modern, interactive quiz platform designed to make quiz nights more engaging and accessible. The brand emphasizes fun, community, and technology-driven entertainment.

## Brand Values

- **Modern**: Cutting-edge technology with intuitive design
- **Engaging**: Interactive features that keep participants involved
- **Community**: Bringing people together through shared experiences
- **Reliable**: Robust platform that works when you need it
- **Fun**: Lighthearted approach to learning and competition

## Color Palette

### Primary Colors
- **Purple Primary**: `#7c3aed` (Purple-600)
- **Blue Secondary**: `#2563eb` (Blue-600)
- **Purple Dark**: `#5b21b6` (Purple-800)
- **Blue Dark**: `#1d4ed8` (Blue-700)

### Gradient Combinations
- **Primary Gradient**: `from-purple-600 to-blue-600`
- **Dark Gradient**: `from-purple-900 via-blue-900 to-purple-800`
- **Hover Gradient**: `from-purple-700 to-blue-700`

### Supporting Colors
- **Success**: `#16a34a` (Green-600)
- **Warning**: `#ea580c` (Orange-600)
- **Danger**: `#dc2626` (Red-600)
- **Neutral**: `#6b7280` (Gray-500)

## Typography

### Headings
- **H1**: `text-4xl md:text-5xl font-bold` (Brand headers)
- **H2**: `text-2xl font-semibold` (Section headers)
- **H3**: `text-xl font-semibold` (Card titles)

### Body Text
- **Primary**: `text-base` (Default body text)
- **Secondary**: `text-sm text-gray-600 dark:text-gray-300` (Descriptions)
- **Large**: `text-lg` (Emphasized text)

## Design System Components

### BrandHeader
The main brand component used for page headers and introductions.

```tsx
<BrandHeader 
  title="QuizNight"
  subtitle="Modern Pub Quiz Platform"
  showLogo={true}
  className="mb-12"
/>
```

### QuizNightButton
Consistent button styling across the application.

```tsx
<QuizNightButton
  variant="primary" // primary, secondary, success, danger, outline
  size="md" // sm, md, lg
  onClick={handleClick}
>
  Button Text
</QuizNightButton>
```

### QuizNightCard
Container component for content sections.

```tsx
<QuizNightCard
  title="Card Title"
  subtitle="Card subtitle"
  variant="elevated" // default, elevated, outlined
>
  Card content
</QuizNightCard>
```

## Iconography

### Emoji Usage
- **👑**: Quiz Master / Host features
- **🎮**: Participant / Player features
- **🤖**: AI-powered features
- **⚡**: Real-time features
- **🌙**: QuizNight brand identity
- **📊**: Analytics and scoring
- **🎯**: Quiz questions and answers

## Layout Guidelines

### Spacing
- **Section spacing**: `mb-12` (48px)
- **Card spacing**: `gap-8` (32px)
- **Component spacing**: `mb-6` (24px)
- **Text spacing**: `mb-2` (8px)

### Container Widths
- **Small**: `max-w-2xl` (672px)
- **Medium**: `max-w-4xl` (896px)
- **Large**: `max-w-6xl` (1152px)

## Responsive Design

### Breakpoints
- **Mobile**: `< 768px`
- **Tablet**: `768px - 1024px`
- **Desktop**: `> 1024px`

### Mobile-First Approach
- Start with mobile layouts
- Use responsive utilities for larger screens
- Ensure touch-friendly button sizes (minimum 44px)

## Dark Mode Support

All components support dark mode with appropriate color adjustments:
- Light backgrounds become dark
- Text colors adapt for readability
- Borders and shadows adjust for contrast

## Animation Guidelines

### Transitions
- **Duration**: `duration-200` (200ms)
- **Easing**: Default Tailwind easing
- **Hover effects**: Subtle scale and shadow changes

### Micro-interactions
- Button hover states
- Card elevation changes
- Loading states with brand colors

## Accessibility

### Color Contrast
- All text meets WCAG AA standards
- High contrast ratios for readability
- Color is not the only indicator of information

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Focus indicators use brand colors
- Logical tab order

### Screen Reader Support
- Semantic HTML structure
- Descriptive alt text for images
- ARIA labels where needed

## Implementation Notes

### CSS Classes
Use Tailwind CSS classes for consistent styling:
- Brand colors: `text-purple-600`, `bg-blue-600`
- Gradients: `bg-gradient-to-r from-purple-600 to-blue-600`
- Shadows: `shadow-lg`, `hover:shadow-xl`

### Component Props
All branded components accept standard props:
- `className`: Additional CSS classes
- `onClick`: Event handlers
- `disabled`: Disabled states
- `variant`: Style variations

## File Structure

```
client/src/components/
├── BrandHeader.tsx      # Main brand header
├── QuizNightButton.tsx  # Branded button component
├── QuizNightCard.tsx    # Branded card component
└── ...
```

## Future Brand Extensions

### Logo Development
- Vector logo in SVG format
- Multiple sizes for different contexts
- Favicon and app icon versions

### Brand Assets
- Social media templates
- Presentation templates
- Marketing materials

### Voice and Tone
- Friendly and approachable
- Technical but accessible
- Encouraging and supportive 