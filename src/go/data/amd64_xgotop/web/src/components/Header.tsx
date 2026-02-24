import { Settings } from 'lucide-react';
import { Button } from './ui/Button';

interface HeaderProps {
  onSettingsClick: () => void;
}

export function Header({ onSettingsClick }: HeaderProps) {
  return (
    <header className="border-b-4 border-black p-4 bg-primary text-primary-foreground">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-black uppercase tracking-wider">xgotop</h1>
        <Button
          onClick={onSettingsClick}
          className="flex items-center gap-2"
          title="Settings"
        >
          <Settings size={20} />
          <span>Settings</span>
        </Button>
      </div>
    </header>
  );
}