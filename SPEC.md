# Network Config Transpiler - SPEC.md

## Concept & Vision

A sleek, professional network configuration deployment interface that transforms pseudo-XML network configurations into deployable configurations. The experience should feel like a premium NMS (Network Management System) dashboard - authoritative, precise, and mission-critical. Users paste their network config in XML format on the left, and the system generates and deploys configurations with real-time progress visualization on the right.

The deployment process is presented as a native "push configuration" workflow - not revealing Ansible under the hood. Progress bars, connection status, and success/failure states create the feeling of a purpose-built deployment engine.

## Design Language

### Aesthetic Direction
Industrial NMS aesthetic - think Cisco DNA Center meets VS Code. Dark slate backgrounds with sharp contrasts, monospace fonts for data, subtle gradients suggesting depth. Professional, not playful.

### Color Palette
- **Background Primary**: `#0f172a` (slate-900)
- **Background Secondary**: `#1e293b` (slate-800)
- **Background Tertiary**: `#334155` (slate-700)
- **Border**: `#475569` (slate-600)
- **Text Primary**: `#f1f5f9` (slate-100)
- **Text Secondary**: `#94a3b8` (slate-400)
- **Accent Primary**: `#3b82f6` (blue-500) - actions, active states
- **Accent Glow**: `#60a5fa` (blue-400) - hover states
- **Success**: `#22c55e` (green-500)
- **Warning**: `#f59e0b` (amber-500)
- **Error**: `#ef4444` (red-500)
- **Progress Track**: `#1e293b`

### Typography
- **Headings**: Inter (Google Fonts), weight 600-700
- **Body**: Inter, weight 400
- **Code/Data**: JetBrains Mono (Google Fonts), weight 400
- **Base size**: 14px
- **Code size**: 13px

### Spatial System
- Base unit: 4px
- Panel padding: 24px
- Component gap: 16px
- Border radius: 8px (panels), 6px (buttons), 4px (inputs)

### Motion Philosophy
- Smooth, professional transitions (200-300ms ease-out)
- Progress bars: linear animation with subtle pulse on active
- Toast notifications: slide-in from top-right, 300ms ease-out
- Tab switches: crossfade 200ms
- Deployment status: sequential reveal with staggered timing

### Visual Assets
- Icons: Lucide Icons (CDN) - clean, consistent stroke weight
- No images required - pure UI
- Subtle box shadows for depth (`0 4px 6px -1px rgba(0,0,0,0.3)`)

## Layout & Structure

### Overall Layout
Full viewport height, no scroll on outer container. Split-screen design:

```
┌─────────────────────────────────────────────────────────────┐
│  Header: Logo + Title + Status Indicator                    │
├───────────────────────────┬─────────────────────────────────┤
│                           │  [Inventory] [Playbook] [Deploy] │
│   INPUT PANEL             │  ─────────────────────────────  │
│   Code Editor             │                                 │
│   (XML Input)             │   OUTPUT PANEL                   │
│                           │   (Tabbed content)               │
│                           │                                 │
│                           │   Deployment Progress            │
│                           │   (when deploying)               │
├───────────────────────────┴─────────────────────────────────┤
│  Footer: Connection Status + Version                         │
└─────────────────────────────────────────────────────────────┘
```

### Responsive Strategy
- Desktop (>1024px): Side-by-side split (50/50)
- Tablet (768-1024px): Side-by-side with reduced padding
- Mobile (<768px): Stacked vertically, input above output

## Features & Interactions

### 1. XML Code Editor (Left Panel)
- Large textarea with syntax highlighting via CodeMirror
- Line numbers visible
- Custom dark theme matching the UI
- Placeholder text showing example XML format
- Auto-indentation on newline
- Tab key inserts 2 spaces (not focus change)

### 2. Generate Button
- Primary action button in header area
- States: Default (blue), Hover (lighter blue + glow), Loading (spinner + "Generating...")
- Click triggers:
  1. Parse XML input
  2. Validate structure
  3. Generate inventory and playbook
  4. Display in output panel
  5. Enable Deploy tab

### 3. Output Tabs (Right Panel)
- **Inventory Tab**: JSON format, grouped by OS
- **Playbook Tab**: YAML format, syntax highlighted
- **Deploy Tab**: Deployment progress visualization

### 4. Deployment Simulation
When user clicks "Deploy Configuration":
- Simulated connection phase (2s)
- Per-device progress bars showing percentage
- Sequential deployment feel (devices process one at a time)
- Each device shows: IP, OS, status (pending → connecting → pushing → success/failed)
- Final summary: X/Y devices successful, elapsed time

### 5. Error Handling
- Invalid XML: Red toast with specific parse error location
- Empty input: Yellow toast "Please enter configuration XML"
- Deployment failures: Individual device status changes to red with error message

### 6. Copy Functionality
- Copy button on each output panel
- Visual feedback: button briefly shows "Copied!" with checkmark

## Component Inventory

### Header Bar
- Height: 64px
- Background: slate-800 with bottom border slate-700
- Logo: Terminal icon (Lucide) + "NetDeploy" text
- Right side: Connection status indicator (green dot + "Ready")

### Code Editor Panel
- Full height minus header/footer
- Header bar inside: "Configuration XML" label + line/char count
- CodeMirror instance with custom theme
- Resize handle on right edge (subtle)

### Output Panel
- Tabs bar: Three tabs with icons
  - Inventory (file-json icon)
  - Playbook (file-code icon)
  - Deploy (rocket icon)
- Active tab: blue underline, white text
- Inactive tab: no underline, slate-400 text
- Tab content: scrollable code block

### Code Block (Output)
- Background: slate-900
- Border: 1px slate-700
- Border-radius: 6px
- Padding: 16px
- Font: JetBrains Mono 13px
- Copy button: top-right corner, slate-600 background

### Deploy Panel
- Device cards in vertical stack
- Each card shows:
  - Target name (bold)
  - IP address (mono)
  - OS badge (eos/nxos/iosxe)
  - Progress bar (animated)
  - Status text

### Progress Bar
- Track: slate-700, height 8px, rounded
- Fill: gradient blue-500 to blue-400
- Animation: width transition 300ms + subtle pulse on active

### Toast Notification
- Fixed position: top-right, 24px from edges
- Width: 360px max
- Variants:
  - Success: green-500 left border, green icon
  - Error: red-500 left border, red icon
  - Warning: amber-500 left border, amber icon
- Auto-dismiss: 5 seconds
- Manual dismiss: X button

### Buttons
- Primary: blue-500 bg, white text, hover blue-400
- Secondary: slate-700 bg, slate-200 text, hover slate-600
- Sizes: sm (28px height), md (36px height), lg (44px height)
- Disabled: 50% opacity, cursor not-allowed

## Technical Approach

### Stack
- Single HTML file, no build step
- Tailwind CSS via CDN (play.tailwindcss.com)
- CodeMirror 6 via CDN for syntax highlighting
- Vanilla JavaScript (ES6+)
- Google Fonts: Inter, JetBrains Mono

### XML Parsing Strategy
1. Use DOMParser to parse input
2. Custom validator for expected structure
3. Extract device configs into intermediate JSON structure
4. Transform to Ansible inventory/playbook format internally

### Pseudo-XML Format Supported
```xml
<config target="router1" host="10.1.1.1" os="eos" user="admin" password="secret">
  <interface name="Loopback0">
    <ip>10.0.0.1/32</ip>
    <state>present</state>
  </interface>
  <bgp as="65001">
    <neighbor ip="10.0.0.2" remote-as="65002">
      <description>ebgp-peer</description>
    </neighbor>
  </bgp>
</config>
```

### Supported Elements
- `config` - device container (target, host, os, user, password)
- `interface` - name attribute, children: ip, state, description
- `vlan` - id attribute, children: name, state
- `bgp` - as attribute
- `neighbor` - ip, remote-as attributes, child: description
- `ospf` - process-id, area attributes
- `network` - ip, area attributes

### Output Format (Internal/Generated)
**Inventory (JSON)**:
```json
{
  "eos": {
    "hosts": {
      "router1": {
        "ansible_host": "10.1.1.1",
        "ansible_user": "admin"
      }
    }
  }
}
```

**Playbook (YAML)**:
```yaml
- name: Configure network devices
  hosts: all
  gather_facts: false
  tasks:
    - name: Configure interface Loopback0
      arista.eos.eos_l3_interface:
        ...
```

### Deployment Visualization
- Simulated 3-5 second deployment per device
- Random success/failure (10% failure rate for realism)
- Realistic phase timing:
  - Connecting: 20%
  - Authenticating: 20%
  - Pushing config: 40%
  - Validating: 20%
