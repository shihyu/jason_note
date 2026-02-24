import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { useConfigStore, type BoxHeightSize } from '../store/configStore';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { boxHeightSize, setBoxHeightSize, exitedGoroutineCleanupTime, setExitedGoroutineCleanupTime } = useConfigStore();

  const handleSizeChange = (size: BoxHeightSize) => {
    setBoxHeightSize(size);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Settings" maxWidth="max-w-xl">
      <div className="space-y-6">
        {/* Box Height Settings */}
        <div>
          <h3 className="text-lg font-bold uppercase mb-3">Timeline Box Heights</h3>
          <div className="flex gap-2">
            <Button
              onClick={() => handleSizeChange('compact')}
              variant={boxHeightSize === 'compact' ? 'default' : 'secondary'}
            >
              Compact
            </Button>
            <Button
              onClick={() => handleSizeChange('normal')}
              variant={boxHeightSize === 'normal' ? 'default' : 'secondary'}
            >
              Normal
            </Button>
            <Button
              onClick={() => handleSizeChange('large')}
              variant={boxHeightSize === 'large' ? 'default' : 'secondary'}
            >
              Large
            </Button>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Adjust the height of goroutine timeline boxes for better space efficiency.
          </p>
        </div>

        {/* Exited Goroutine Cleanup Time */}
        <div>
          <h3 className="text-lg font-bold uppercase mb-3">Cleanup Settings</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-bold uppercase mb-2">
                Exited Goroutine Cleanup Time (seconds)
              </label>
              <input
                type="number"
                min="1"
                max="60"
                value={exitedGoroutineCleanupTime}
                onChange={(e) => {
                  const value = parseInt(e.target.value);
                  if (value > 0 && value <= 60) {
                    setExitedGoroutineCleanupTime(value);
                  }
                }}
                className="w-24 px-3 py-2 border-2 border-black font-mono"
              />
              <p className="text-xs text-gray-600 mt-1">
                Time to keep exited goroutines visible (when preserve is unchecked)
              </p>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
}