import { Button } from './ui/Button';

export type TabView = 'timeline' | 'memory';

interface TabsProps {
  activeTab: TabView;
  onTabChange: (tab: TabView) => void;
}

export function Tabs({ activeTab, onTabChange }: TabsProps) {
  return (
    <div className="px-4 pb-2">
      <div className="flex gap-2">
        <Button
          onClick={() => onTabChange('timeline')}
          variant={activeTab === 'timeline' ? 'default' : 'secondary'}
          className="uppercase font-bold"
        >
          Timeline View
        </Button>
        <Button
          onClick={() => onTabChange('memory')}
          variant={activeTab === 'memory' ? 'default' : 'secondary'}
          className="uppercase font-bold"
        >
          Memory View
        </Button>
      </div>
    </div>
  );
}