#!/bin/bash

# clean.sh - Cleanup script for Arcade Flow Analyzer
# Removes all generated files, cache, logs, and temporary data

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Cleaning up Arcade Flow Analyzer project..."
echo "Project root: $PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to safely remove directory contents
clean_directory() {
    local dir_path="$1"
    local description="$2"

    if [ -d "$dir_path" ]; then
        echo -e "${YELLOW}Cleaning $description...${NC}"

        # Count files before cleaning
        file_count=$(find "$dir_path" -type f 2>/dev/null | wc -l || echo "0")

        if [ "$file_count" -gt 0 ]; then
            # Remove all files in directory but keep the directory structure
            find "$dir_path" -type f -delete 2>/dev/null || true
            echo -e "${GREEN}  Removed $file_count files from $dir_path${NC}"
        else
            echo -e "${GREEN}  $dir_path is already clean${NC}"
        fi
    else
        echo -e "${YELLOW}  $dir_path does not exist, skipping${NC}"
    fi
}

# Function to remove files by pattern
remove_files() {
    local pattern="$1"
    local description="$2"

    echo -e "${YELLOW}Removing $description...${NC}"

    # Use find to locate and count files matching pattern
    found_files=$(find . -name "$pattern" -type f 2>/dev/null | wc -l || echo "0")

    if [ "$found_files" -gt 0 ]; then
        find . -name "$pattern" -type f -delete 2>/dev/null || true
        echo -e "${GREEN}  Removed $found_files files matching pattern: $pattern${NC}"
    else
        echo -e "${GREEN}  No files found matching pattern: $pattern${NC}"
    fi
}

echo ""
echo "Cleaning generated files and cache..."

# Clean cache directory (API responses)
clean_directory ".cache" "API response cache"

# Clean results/output directory
clean_directory "results" "generated reports and images"
clean_directory "output" "generated reports and images (old location)"

# Clean logs directory
clean_directory "logs" "application logs"

# Clean processed data
clean_directory "data/processed" "processed data files"

echo ""
echo "Cleaning Python artifacts..."

# Clean Python cache files
remove_files "*.pyc" "Python bytecode files"
remove_files "*.pyo" "Python optimized bytecode files"
clean_directory "__pycache__" "Python cache directories"
find . -name "__pycache__" -type d -delete 2>/dev/null || true

# Clean pytest cache
clean_directory ".pytest_cache" "pytest cache"

# Clean mypy cache
clean_directory ".mypy_cache" "mypy cache"

echo ""
echo "Cleaning other temporary files..."

# Clean any remaining log files in root
remove_files "*.log" "log files"

# Clean temporary files
remove_files "*.tmp" "temporary files"
remove_files "*.temp" "temporary files"
remove_files "*~" "backup files"

# Clean editor files
remove_files "*.swp" "vim swap files"
remove_files "*.swo" "vim swap files"
remove_files ".DS_Store" "macOS metadata files"

echo ""
echo "Cleaning development artifacts..."

# Clean coverage reports
clean_directory "htmlcov" "coverage HTML reports"
remove_files ".coverage" "coverage data files"
remove_files ".coverage.*" "coverage data files"
remove_files "coverage.xml" "coverage XML reports"

# Clean distribution files
clean_directory "dist" "distribution files"
clean_directory "build" "build artifacts"
clean_directory "*.egg-info" "egg info directories"
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "Cleanup summary:"

# Final statistics
total_dirs=0
total_files=0

for dir in .cache results output logs data/processed __pycache__ .pytest_cache .mypy_cache htmlcov dist build; do
    if [ -d "$dir" ]; then
        dir_files=$(find "$dir" -type f 2>/dev/null | wc -l || echo "0")
        echo -e "${GREEN}  $dir: $dir_files files remaining${NC}"
        total_files=$((total_files + dir_files))
        total_dirs=$((total_dirs + 1))
    fi
done

echo ""
if [ "$total_files" -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS] Project is completely clean!${NC}"
else
    echo -e "${YELLOW}[INFO] $total_files files remaining in $total_dirs directories${NC}"
fi

echo ""
echo -e "${GREEN}[SUCCESS] Cleanup complete!${NC}"
echo ""
echo "To regenerate files, run:"
echo "  poetry run analyze-flow"
echo ""