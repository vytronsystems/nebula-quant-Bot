package com.nebulaquant.controlplane.repository;

import com.nebulaquant.controlplane.domain.InstrumentRegistry;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface InstrumentRegistryRepository extends JpaRepository<InstrumentRegistry, UUID> {

    List<InstrumentRegistry> findByVenueOrderBySymbolAsc(String venue);

    List<InstrumentRegistry> findByVenueAndActiveOrderBySymbolAsc(String venue, boolean active);

    List<InstrumentRegistry> findByActiveOrderByVenueAscSymbolAsc(boolean active);

    List<InstrumentRegistry> findAllByOrderByVenueAscSymbolAsc();

    Optional<InstrumentRegistry> findByVenueAndSymbol(String venue, String symbol);
}
