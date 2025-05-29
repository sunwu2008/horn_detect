Detect and log all segments in the full MP3 that match the sample with similarity above a chosen threshold.
it can detect horn and mark all the times.

python log_merge.py --i match_log.txt --o logall.txt --gap_ms 3000 
merge the all lines within 3000ms to one line(assuming horn lasts 3s)
