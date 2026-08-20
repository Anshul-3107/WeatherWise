class AdviceModel {
  final String profile;
  final String advice;

  AdviceModel({
    required this.profile,
    required this.advice,
  });

  factory AdviceModel.fromJson(Map<String, dynamic> json) {
    return AdviceModel(
      profile: json['profile'] as String,
      advice: json['advice'] as String,
    );
  }
}