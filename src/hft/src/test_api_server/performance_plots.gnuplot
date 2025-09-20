# Gnuplot script for performance comparison visualization

# General settings
set terminal pngcairo enhanced font 'Arial,12' size 1200,800
set grid

# Create output directory
system "mkdir -p performance_plots"

# 1. Throughput Comparison Bar Chart
set output 'performance_plots/throughput_comparison.png'
set title 'Throughput Comparison (Higher is Better)' font 'Arial,16'
set xlabel 'Client Implementation' font 'Arial,14'
set ylabel 'Throughput (requests/second)' font 'Arial,14'
set style data histogram
set style histogram clustered gap 1
set style fill solid 0.8 border -1
set boxwidth 0.8
set xtic rotate by -45 scale 0
set yrange [0:*]
set key off

# Add error bars for standard deviation
set style histogram errorbars gap 1 lw 2
plot 'performance_data/throughput.dat' using 2:3:xtic(1) with histogram title '' lc rgb "#4472C4"

# 2. Latency Percentiles Comparison
set output 'performance_plots/latency_percentiles.png'
set title 'Latency Percentiles Comparison (Lower is Better)' font 'Arial,16'
set xlabel 'Client Implementation' font 'Arial,14'
set ylabel 'Latency (ms)' font 'Arial,14'
set style data histogram
set style histogram clustered gap 1
set style fill solid 0.8 border -1
set boxwidth 0.2
set xtic rotate by -45 scale 0
set yrange [0:*]
set key top left
set key font 'Arial,11'

plot 'performance_data/latency_percentiles.dat' using 2:xtic(1) title 'P50' lc rgb "#4472C4", \
     '' using 3 title 'P90' lc rgb "#ED7D31", \
     '' using 4 title 'P95' lc rgb "#A5A5A5", \
     '' using 5 title 'P99' lc rgb "#FFC000"

# 3. Latency Range Comparison (Min, Avg, Max)
set output 'performance_plots/latency_range.png'
set title 'Latency Range Comparison' font 'Arial,16'
set xlabel 'Client Implementation' font 'Arial,14'
set ylabel 'Latency (ms)' font 'Arial,14'
set style data histogram
set style histogram clustered gap 1
set style fill solid 0.8 border -1
set boxwidth 0.25
set xtic rotate by -45 scale 0
set yrange [0:*]
set key top left
set key font 'Arial,11'

plot 'performance_data/latency_comparison.dat' using 2:xtic(1) title 'Min Latency' lc rgb "#70AD47", \
     '' using 3 title 'Avg Latency' lc rgb "#4472C4", \
     '' using 4 title 'Max Latency' lc rgb "#C55A11"

# 4. Combined Throughput and Latency Chart (dual Y-axis)
set output 'performance_plots/throughput_vs_latency.png'
set title 'Throughput vs Average Latency' font 'Arial,16'
set xlabel 'Client Implementation' font 'Arial,14'
set ylabel 'Throughput (req/s)' font 'Arial,14' textcolor rgb "#4472C4"
set y2label 'Average Latency (ms)' font 'Arial,14' textcolor rgb "#ED7D31"
set y2tics
set ytics nomirror
set style data histogram
set style histogram clustered gap 2
set style fill solid 0.8 border -1
set boxwidth 0.4
set xtic rotate by -45 scale 0
set key top left
set key font 'Arial,11'

plot 'performance_data/throughput.dat' using 2:xtic(1) title 'Throughput' axes x1y1 lc rgb "#4472C4" with boxes, \
     'performance_data/latency_comparison.dat' using 3 title 'Avg Latency' axes x1y2 lc rgb "#ED7D31" with boxes

# 5. Performance Summary Comparison
set output 'performance_plots/performance_summary.png'
set title 'Performance Summary' font 'Arial,16'
set xlabel 'Client Implementation' font 'Arial,14'
set ylabel 'Value' font 'Arial,14'
set style data histogram
set style histogram clustered gap 1
set style fill solid 0.8 border -1
set boxwidth 0.9
set xtic rotate by -45 scale 0
set yrange [0:*]
set key off

# Just plot throughput as summary
plot 'performance_data/throughput.dat' using 2:xtic(1) with boxes lc rgb "#4472C4"

# 6. Box Plot for Latency Distribution (if we had raw data)
# Would need raw latency data points, not just percentiles

# Reset to default
unset polar
unset rrange
unset trange
set y2tics
set y2label
set ytics mirror
set xtics
set ytics

# 7. Time Series of Performance Across Runs
set output 'performance_plots/time_series.png'
set title 'Performance Across Test Runs' font 'Arial,16'
set xlabel 'Test Run Number' font 'Arial,14'
set ylabel 'Throughput (req/s)' font 'Arial,14'
set y2label 'Latency (ms)' font 'Arial,14'
set y2tics
set ytics nomirror
set grid
set key outside right
set key font 'Arial,10'

# Get column count for dynamic plotting
stats 'performance_data/time_series.dat' nooutput
ncols = STATS_columns

# Plot throughput on y1 axis and latency on y2 axis
# Simple plot for 2 clients
plot 'performance_data/time_series.dat' using 1:2 with linespoints \
     title "Python Throughput" axes x1y1 lc rgb "#4472C4" pt 7 ps 1.5, \
     '' using 1:3 with linespoints \
     title "Python Latency" axes x1y2 lc rgb "#ED7D31" pt 5 ps 1.5 dt 2, \
     '' using 1:4 with linespoints \
     title "C Throughput" axes x1y1 lc rgb "#70AD47" pt 7 ps 1.5, \
     '' using 1:5 with linespoints \
     title "C Latency" axes x1y2 lc rgb "#FFC000" pt 5 ps 1.5 dt 2

# 8. Performance Summary Table (as image)
set output 'performance_plots/summary_table.png'
set title 'Performance Summary Statistics' font 'Arial,16'
unset xlabel
unset ylabel
unset y2label
unset y2tics
unset xtics
unset ytics
unset grid
unset key

# Create a simple comparison chart with values
set label 1 "Performance data saved in performance_data/" at screen 0.5,0.5 center font 'Arial,14'
set label 2 "Run 'compare_performance.py' to generate fresh data" at screen 0.5,0.4 center font 'Arial,12'
plot NaN

# Clean up
unset label 1
unset label 2

print "All plots generated successfully in performance_plots/"