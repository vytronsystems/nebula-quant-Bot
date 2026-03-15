package com.nebulaquant.controlplane.repository;

import com.nebulaquant.controlplane.domain.PromotionReview;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface PromotionReviewRepository extends JpaRepository<PromotionReview, UUID> {
}
