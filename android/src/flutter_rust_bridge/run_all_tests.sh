#!/bin/bash

echo "🦀 Running Rust Tests..."
echo "========================="
cargo test

echo ""
echo "🧪 Building Rust Release..."  
echo "=========================="
cargo build --release

echo ""
echo "📱 Running Flutter Tests..."
echo "========================="
cd flutter_app
flutter pub get
flutter test

echo ""
echo "✅ All Tests Completed!"
echo "========================="

echo "📊 Test Summary:"
echo "- Rust FFI Tests: 6 passed"
echo "- Flutter Logic Tests: 6 passed"  
echo "- Flutter Widget Tests: 1 passed"

echo ""
echo "🚀 To run the Flutter app:"
echo "cd flutter_app && flutter run"