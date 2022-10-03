SELECT sanitized_text,
       COUNT(sanitized_text) AS occurrences,
       SUM(100.0 * COUNT(sanitized_text) / (SELECT COUNT(*) FROM messages)) OVER
         (ORDER BY COUNT(sanitized_text) DESC) as cummulative_percentage
  FROM messages JOIN sanitized_messages USING (text)
 WHERE rank = 1
 GROUP BY sanitized_text
 ORDER BY COUNT(sanitized_text) DESC;
