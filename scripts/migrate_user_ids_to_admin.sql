-- 迁移所有表的 user_id 为 admin
-- 执行前请确保已备份数据库

-- 已有user_id的表
UPDATE conversations SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE reminders SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE tasks SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE user_behaviors SET user_id = 'admin' WHERE user_id != 'admin';

-- 其他包含user_id的表
UPDATE documents SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE face_encodings SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE knowledge_nodes SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE learned_patterns SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE learning_preferences SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE learning_progress SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE message_feedback SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE proactive_questions SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE reminder_history SET user_id = 'admin' WHERE user_id != 'admin';
UPDATE tool_executions SET user_id = 'admin' WHERE user_id != 'admin';

-- 验证结果：显示所有表中admin用户的记录数
SELECT 'conversations' as table_name, COUNT(*) as admin_count FROM conversations WHERE user_id = 'admin'
UNION ALL SELECT 'reminders', COUNT(*) FROM reminders WHERE user_id = 'admin'
UNION ALL SELECT 'tasks', COUNT(*) FROM tasks WHERE user_id = 'admin'
UNION ALL SELECT 'user_behaviors', COUNT(*) FROM user_behaviors WHERE user_id = 'admin'
UNION ALL SELECT 'documents', COUNT(*) FROM documents WHERE user_id = 'admin'
UNION ALL SELECT 'face_encodings', COUNT(*) FROM face_encodings WHERE user_id = 'admin'
UNION ALL SELECT 'knowledge_nodes', COUNT(*) FROM knowledge_nodes WHERE user_id = 'admin'
UNION ALL SELECT 'learned_patterns', COUNT(*) FROM learned_patterns WHERE user_id = 'admin'
UNION ALL SELECT 'learning_preferences', COUNT(*) FROM learning_preferences WHERE user_id = 'admin'
UNION ALL SELECT 'learning_progress', COUNT(*) FROM learning_progress WHERE user_id = 'admin'
UNION ALL SELECT 'message_feedback', COUNT(*) FROM message_feedback WHERE user_id = 'admin'
UNION ALL SELECT 'proactive_questions', COUNT(*) FROM proactive_questions WHERE user_id = 'admin'
UNION ALL SELECT 'reminder_history', COUNT(*) FROM reminder_history WHERE user_id = 'admin'
UNION ALL SELECT 'tool_executions', COUNT(*) FROM tool_executions WHERE user_id = 'admin'
ORDER BY table_name;
