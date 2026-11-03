import 'activity.dart' show UserPublic;

class Comment {
  final String id;
  final String activityId;
  final String content;
  final DateTime createdAt;
  final DateTime updatedAt;
  final UserPublic? author;

  Comment({
    required this.id,
    required this.activityId,
    required this.content,
    required this.createdAt,
    required this.updatedAt,
    this.author,
  });

  factory Comment.fromJson(Map<String, dynamic> json) {
    return Comment(
      id: json['id'] as String,
      activityId: json['activity_id'] as String,
      content: (json['content'] ?? '') as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.parse(json['created_at'] as String),
      author: json['author'] != null
          ? UserPublic.fromJson(json['author'] as Map<String, dynamic>)
          : null,
    );
  }

  Comment copyWith({
    String? content,
    DateTime? updatedAt,
    UserPublic? author,
  }) {
    return Comment(
      id: id,
      activityId: activityId,
      content: content ?? this.content,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      author: author ?? this.author,
    );
  }

  /// Só o autor do comentário pode deletar (regra do backend).
  bool canDelete(String? currentUserId) {
    return currentUserId != null && author?.id == currentUserId;
  }
}